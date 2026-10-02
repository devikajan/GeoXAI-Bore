import unittest
from fastapi.testclient import TestClient
from backend.main import app


class DrillingTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def check_depth(self, planned, water_table):
        response = self.client.post('/drilling/assess', json={
            'planned_depth_ft': planned, 'estimated_water_table_ft': water_table,
        })
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIsNone(result['success_probability'])
        return result

    def test_reaching_water_table_does_not_claim_success(self):
        result = self.check_depth(450, 280)
        self.assertEqual(result['depth_check'], 'passes')
        self.assertEqual(result['depth_margin_ft'], 170)
        self.assertIn('unconfirmed', result['limitation'])

    def test_shortfall_and_equal_depth_require_review(self):
        for planned, water_table, margin in [(200, 280, -80), (280, 280, 0)]:
            with self.subTest(planned=planned):
                result = self.check_depth(planned, water_table)
                self.assertEqual(result['depth_check'], 'review_required')
                self.assertEqual(result['depth_margin_ft'], margin)

    def test_invalid_depths(self):
        for value in [0, -1, 1501]:
            response = self.client.post('/drilling/assess', json={
                'planned_depth_ft': value, 'estimated_water_table_ft': 280,
            })
            self.assertEqual(response.status_code, 422)

    def test_drilling_context_is_accepted_without_maintenance_score(self):
        from backend.main import ChatRequest
        request = ChatRequest(messages=[{'role': 'user', 'content': 'Explain this'}],
                              assessment=self.check_depth(450, 280))
        self.assertEqual(request.assessment.assessment_type, 'drilling')


if __name__ == '__main__':
    unittest.main()
