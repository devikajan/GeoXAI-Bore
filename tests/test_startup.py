import unittest
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from backend.main import app


class StartupTests(unittest.TestCase):
    def test_startup_keeps_health_available_and_explainer_is_shared(self):
        from backend.explain import get_explainer
        with TestClient(app) as client:
            self.assertEqual(client.get('/health').json()['status'], 'healthy')
            with ThreadPoolExecutor(max_workers=3) as pool:
                explainers = list(pool.map(lambda _: get_explainer(), range(3)))
            self.assertTrue(all(item is explainers[0] for item in explainers))
