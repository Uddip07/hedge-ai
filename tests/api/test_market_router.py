"""
Unit tests for GET /market/{ticker} API endpoint.
"""

import unittest

from fastapi.testclient import TestClient

from packages.api.main import app


class TestMarketRouter(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_get_market_data_valid_bare_ticker(self) -> None:
        response = self.client.get("/market/RELIANCE")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["ticker"], "RELIANCE.NSE")
        self.assertTrue(float(data["price"]) > 0)
        self.assertEqual(data["currency"], "INR")
        self.assertTrue(len(data["company_name"]) > 0)
        self.assertIsInstance(data["is_market_open"], bool)

    def test_get_market_data_valid_ticker_with_exchange(self) -> None:
        response = self.client.get("/market/TCS.NSE")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["ticker"], "TCS.NSE")
        self.assertIsNotNone(data["price"])

    def test_get_market_data_invalid_ticker_format_fails(self) -> None:
        response = self.client.get("/market/INVALID_TICKER_SYMBOL_TOO_LONG")
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], "HTTP_422")


if __name__ == "__main__":
    unittest.main()
