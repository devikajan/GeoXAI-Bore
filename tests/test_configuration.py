import os
import unittest
from unittest.mock import patch

from backend.main import LOCAL_CORS_ORIGINS, resolve_cors_origins


class ConfigurationTests(unittest.TestCase):
    @patch("backend.main.dotenv_values", return_value={})
    def test_local_origins_are_available_by_default(self, _dotenv_values):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(resolve_cors_origins(), list(LOCAL_CORS_ORIGINS))

    @patch("backend.main.dotenv_values", return_value={})
    def test_deployment_origins_are_added_and_normalized(self, _dotenv_values):
        with patch.dict(os.environ, {
            "CORS_ORIGINS": "https://frontend.example/, https://preview.example"
        }, clear=True):
            origins = resolve_cors_origins()
        self.assertIn("https://frontend.example", origins)
        self.assertIn("https://preview.example", origins)
        self.assertNotIn("https://frontend.example/", origins)


if __name__ == "__main__":
    unittest.main()
