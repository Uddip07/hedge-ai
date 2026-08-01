"""
Unit tests for Investment Analysis POST /analyze endpoint.
"""

import unittest

from fastapi.testclient import TestClient

from packages.api.main import app


class TestAnalyzeRouter(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_analyze_stock_valid_ticker_bare(self) -> None:
        response = self.client.post("/analyze", json={"ticker": "RELIANCE"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["ticker"], "RELIANCE.NSE")
        self.assertIn("recommendation", data)
        self.assertIn("consensus_score", data)
        self.assertIn("risk_level", data)
        self.assertTrue(data["is_suitable_for_portfolio"])

    def test_analyze_stock_valid_ticker_with_exchange(self) -> None:
        response = self.client.post("/analyze", json={"ticker": "TCS.NSE"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["ticker"], "TCS.NSE")

    def test_analyze_stock_empty_ticker_fails_validation(self) -> None:
        response = self.client.post("/analyze", json={"ticker": ""})
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], "REQUEST_VALIDATION_ERROR")

    def test_analyze_stock_invalid_ticker_format_fails_use_case_validation(self) -> None:
        response = self.client.post("/analyze", json={"ticker": "INVALID_TICKER_SYMBOL_TOO_LONG"})
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], "VALIDATION_ERROR")


if __name__ == "__main__":
    unittest.main()
