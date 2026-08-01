"""
Unit tests for Health and Status API endpoints.
"""

import unittest

from fastapi.testclient import TestClient

from packages.api.main import app


class TestHealthRouter(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_get_root(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["application"], "MONEYYYYYY")
        self.assertEqual(data["version"], "1.0.0")
        self.assertEqual(data["status"], "running")

    def test_get_health(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["database"], "configured")
        self.assertEqual(data["cache"], "configured")
        self.assertEqual(data["application"], "running")

    def test_get_version(self) -> None:
        response = self.client.get("/version")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "MONEYYYYYY API")
        self.assertEqual(data["version"], "1.0.0")


if __name__ == "__main__":
    unittest.main()
