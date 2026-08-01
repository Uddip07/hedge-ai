"""
Unit tests for API Middlewares and Exception Handlers.
"""

import unittest

from fastapi.testclient import TestClient

from packages.api.main import app


class TestMiddlewareAndExceptions(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_request_id_and_timing_headers(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertIn("X-Request-ID", response.headers)
        self.assertIn("X-Process-Time", response.headers)

    def test_custom_request_id_propagation(self) -> None:
        custom_id = "test-request-id-12345"
        response = self.client.get("/health", headers={"X-Request-ID": custom_id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-Request-ID"], custom_id)

    def test_not_found_endpoint_returns_standard_error(self) -> None:
        response = self.client.get("/non-existent-endpoint")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], "HTTP_404")


if __name__ == "__main__":
    unittest.main()
