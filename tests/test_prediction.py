import unittest

from fastapi.testclient import TestClient

from backend.main import app


VALID_INPUT = {
    "Borewell_Depth_ft": 450,
    "Water_Table_Depth_ft": 280,
    "Pump_Age_years": 4,
    "Daily_Usage_hours": 7,
    "Soil_Type": "Sandy",
    "Region_Type": "Plains",
    "Annual_Rainfall_mm": 900,
    "Maintenance_Frequency_per_year": 1,
    "Motor_Temperature_C": 58,
    "Vibration_Level_mms": 2.2,
    "Voltage_Fluctuation_pct": 8,
    "Water_Yield_LPH": 1200,
    "Casing_Pipe_Age_years": 6,
}


class PredictionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})

    def test_prediction_contract(self):
        response = self.client.post("/predict", json=VALID_INPUT)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn(result["risk_category"], {"Low", "Medium", "High"})
        self.assertGreaterEqual(result["ensemble_probability"], 0)
        self.assertLessEqual(result["ensemble_probability"], 1)
        self.assertEqual(len(result["top_features"]), 5)

    def test_explanation_contract(self):
        response = self.client.post("/explain", json=VALID_INPUT)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["top_features"]), 5)

    def test_invalid_measurements_are_rejected(self):
        invalid_values = {
            "Borewell_Depth_ft": 0,
            "Water_Table_Depth_ft": 1001,
            "Daily_Usage_hours": 25,
            "Motor_Temperature_C": 10,
            "Water_Yield_LPH": -1,
        }
        for field, value in invalid_values.items():
            with self.subTest(field=field):
                response = self.client.post("/predict", json={**VALID_INPUT, field: value})
                self.assertEqual(response.status_code, 422)

    def test_unknown_categories_are_rejected(self):
        for field in ("Soil_Type", "Region_Type"):
            with self.subTest(field=field):
                response = self.client.post("/predict", json={**VALID_INPUT, field: "Unknown"})
                self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
