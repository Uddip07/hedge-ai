"""
Unit tests for GET /company-intelligence/{ticker} endpoint.
"""

import unittest

from fastapi.testclient import TestClient

from packages.api.main import app


class TestCompanyIntelligenceRouter(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_get_company_intelligence(self) -> None:
        response = self.client.get("/company-intelligence/RELIANCE")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["ticker"], "RELIANCE.NSE")
        self.assertIn("company_name", data)
        self.assertIn("executive_summary", data)
        self.assertIn("market_snapshot", data)
        self.assertIn("financial_highlights", data)
        self.assertIn("consensus_decision", data)


if __name__ == "__main__":
    unittest.main()
