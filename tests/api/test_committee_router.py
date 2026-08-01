"""
Unit tests for POST /committee/evaluate endpoint.
"""

import unittest

from fastapi.testclient import TestClient

from packages.api.main import app


class TestCommitteeRouter(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_evaluate_committee(self) -> None:
        payload = {
            "ticker": "INFY.NSE",
            "horizon": "LONG_TERM",
            "style": "VALUE",
            "user_query": "Evaluate long-term investment viability.",
        }
        response = self.client.post("/committee/evaluate", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["ticker"], "INFY.NSE")
        self.assertIn("winning_recommendation", data)
        self.assertIn("consensus_score", data)
        self.assertIn("confidence", data)
        self.assertIn("verdict_summary", data)
        self.assertIn("explanation", data)

    def test_evaluate_committee_validation_error(self) -> None:
        payload = {
            "ticker": "",
        }
        response = self.client.post("/committee/evaluate", json=payload)
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
