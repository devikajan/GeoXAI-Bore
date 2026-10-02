import unittest
from fastapi.testclient import TestClient
from backend.main import app, ChatRequest


class SiteAssessmentTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def assess(self, site_id, target):
        response = self.client.post('/drilling/site-assess', json={
            'site_id': site_id, 'desired_yield_lph': target,
        })
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_reference_catalogue_has_valid_coverage(self):
        response = self.client.get('/drilling/sites')
        self.assertEqual(response.status_code, 200)
        sites = response.json()
        self.assertEqual(len(sites), 26)
        self.assertEqual(len({site['id'] for site in sites}), 26)
        self.assertEqual(len({site['district'] for site in sites}), 20)

    def test_station_units_and_target_comparison(self):
        result = self.assess('kodumuru-apts', 1000)
        self.assertEqual(result['site']['geology'], 'Granite Gniess')
        self.assertEqual(result['reference_yield_lph'], 612)
        self.assertAlmostEqual(result['reference_water_depth_ft'], 9.9)
        self.assertEqual(result['evidence_status'], 'reference_below_target')
        self.assertIsNone(result['success_probability'])
        result = self.assess('kodumuru-apts', 612)
        self.assertEqual(result['evidence_status'], 'reference_meets_target')

    def test_locations_change_evidence_not_maintenance_prediction(self):
        first = self.assess('kodumuru-apts', 1000)
        second = self.assess('kollipara-apts', 1000)
        self.assertNotEqual(first['reference_yield_lph'], second['reference_yield_lph'])
        self.assertNotEqual(first['site']['geology'], second['site']['geology'])
        self.assertNotIn('ensemble_probability', second)
        self.assertIn('not a plot-level prediction', second['limitation'])
        self.assertIsNone(second['site']['measurement_date'])

    def test_unknown_location_and_invalid_target(self):
        self.assertEqual(self.client.post('/drilling/site-assess', json={
            'site_id': 'unknown', 'desired_yield_lph': 1000,
        }).status_code, 404)
        for value in [0, -1, 100001]:
            self.assertEqual(self.client.post('/drilling/site-assess', json={
                'site_id': 'kodumuru-apts', 'desired_yield_lph': value,
            }).status_code, 422)

    def test_location_context_is_available_to_assistant(self):
        request = ChatRequest(messages=[{'role': 'user', 'content': 'Explain this'}],
                              assessment=self.assess('kodumuru-apts', 1000))
        self.assertEqual(request.assessment.assessment_type, 'drilling_site')
        self.assertIsNone(request.assessment.success_probability)
