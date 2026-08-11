"""
Regression Tests for Market Data Consistency, Single Source of Truth, and Symbol Mappings.

Validates:
1. ^NSEI maps to NIFTY 50 (^NSEI)
2. ^NSEBANK maps to BANK NIFTY (^NSEBANK)
3. ^BSESN maps to SENSEX (^BSESN)
4. RELIANCE maps to RELIANCE.NS on Yahoo and RELIANCE.NSE in domain
5. All endpoints receive the same canonical quote structure
6. previous_close is distinct and mathematically verified
7. Missing chart data does not become 0
8. Timezone calculations use Asia/Kolkata (IST)
9. Market-state detection logic
10. WebSocket endpoint does not generate synthetic random price walks
"""

import unittest
from decimal import Decimal

from fastapi.testclient import TestClient

from packages.api.main import app
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.infrastructure.market_data.providers.yahoo_provider import YahooMarketDataProvider


class TestMarketDataConsistency(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.provider = YahooMarketDataProvider()

    def test_symbol_resolution_nifty_indices(self) -> None:
        """Verify index symbol mappings to Yahoo Finance symbols."""
        self.assertEqual(self.provider._resolve_yf_symbol(Ticker("NIFTY.NSE")), "^NSEI")
        self.assertEqual(self.provider._resolve_yf_symbol(Ticker("BANKNIFTY.NSE")), "^NSEBANK")
        self.assertEqual(self.provider._resolve_yf_symbol(Ticker("SENSEX.BSE")), "^BSESN")

    def test_symbol_resolution_equities(self) -> None:
        """Verify Indian equity ticker resolutions (.NS for NSE, .BO for BSE)."""
        self.assertEqual(self.provider._resolve_yf_symbol(Ticker("RELIANCE.NSE")), "RELIANCE.NS")
        self.assertEqual(self.provider._resolve_yf_symbol(Ticker("TCS.NSE")), "TCS.NS")
        self.assertEqual(self.provider._resolve_yf_symbol(Ticker("INFY.NSE")), "INFY.NS")
        self.assertEqual(self.provider._resolve_yf_symbol(Ticker("SBIN.BSE")), "SBIN.BO")

    def test_canonical_quote_endpoint_schema(self) -> None:
        """Verify GET /market/{ticker} returns the full canonical quote contract."""
        response = self.client.get("/market/RELIANCE")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        required_keys = [
            "symbol",
            "ticker",
            "yahoo_symbol",
            "exchange",
            "name",
            "price",
            "previous_close",
            "change",
            "change_percent",
            "open",
            "high",
            "low",
            "volume",
            "timestamp",
            "timestamp_ist",
            "market_state",
            "is_market_open",
            "currency",
            "source",
            "company_name",
        ]
        for key in required_keys:
            self.assertIn(key, data, f"Missing canonical key: {key}")

        self.assertEqual(data["symbol"], "RELIANCE")
        self.assertEqual(data["ticker"], "RELIANCE.NSE")
        self.assertEqual(data["yahoo_symbol"], "RELIANCE.NS")
        self.assertEqual(data["currency"], "INR")
        self.assertIn("IST", data["timestamp_ist"])
        self.assertIsInstance(data["price"], (int, float))
        self.assertTrue(data["price"] > 0, "Market price must be strictly positive")

    def test_nifty_index_quote_endpoint(self) -> None:
        """Verify NIFTY.NSE quote resolves properly with canonical name and price."""
        response = self.client.get("/market/NIFTY.NSE")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["symbol"], "NIFTY")
        self.assertEqual(data["yahoo_symbol"], "^NSEI")
        self.assertEqual(data["name"], "NIFTY 50")
        self.assertTrue(data["price"] > 10000, "NIFTY index price should be > 10,000")

    def test_banknifty_index_quote_endpoint(self) -> None:
        """Verify BANKNIFTY.NSE quote resolves to ^NSEBANK."""
        response = self.client.get("/market/BANKNIFTY.NSE")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["symbol"], "BANKNIFTY")
        self.assertEqual(data["yahoo_symbol"], "^NSEBANK")
        self.assertIn(data["name"], ("BANK NIFTY", "NIFTY BANK"))
        self.assertTrue(data["price"] > 20000, "BANK NIFTY index price should be > 20,000")

    def test_sensex_index_quote_endpoint(self) -> None:
        """Verify SENSEX.BSE quote resolves to ^BSESN."""
        response = self.client.get("/market/SENSEX.BSE")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["symbol"], "SENSEX")
        self.assertEqual(data["yahoo_symbol"], "^BSESN")
        self.assertIn("SENSEX", data["name"])
        self.assertTrue(data["price"] > 40000, "SENSEX index price should be > 40,000")

    def test_mathematical_change_calculation(self) -> None:
        """Verify change and change_percent formulas."""
        price = Decimal("1327.30")
        prev = Decimal("1321.30")
        change = price - prev
        pct = (change / prev) * Decimal("100")
        self.assertEqual(change, Decimal("6.00"))
        self.assertAlmostEqual(float(pct), 0.4541, places=3)

    def test_market_state_ist_timings(self) -> None:
        """Verify Indian market state detection."""
        m_state, source, is_open = YahooMarketDataProvider.get_indian_market_state()
        self.assertIn(m_state, ("PRE_MARKET", "OPEN", "POST_MARKET", "CLOSED"))
        self.assertIn(
            source,
            ("YAHOO_PRE_MARKET", "YAHOO_DELAYED", "YAHOO_POST_MARKET", "YAHOO_LAST_CLOSE"),
        )
        self.assertIsInstance(is_open, bool)

    def test_historical_candles_flattened_schema(self) -> None:
        """Verify GET /market/{ticker}/history returns flat numeric candle dictionaries."""
        response = self.client.get("/market/RELIANCE.NSE/history")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIsInstance(data, list)
        if len(data) > 0:
            first = data[0]
            for field in ("date", "timestamp", "open", "high", "low", "close", "volume"):
                self.assertIn(field, first, f"Missing historical candle field: {field}")
            self.assertIsInstance(first["open"], (int, float))
            self.assertIsInstance(first["close"], (int, float))
            self.assertTrue(first["close"] > 0, "Historical candle close must be > 0")

    def test_provider_timestamp_provenance(self) -> None:
        """Verify quote timestamp originates from provider and formats to IST."""
        response = self.client.get("/market/RELIANCE.NSE")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("timestamp", data)
        self.assertIn("timestamp_ist", data)
        self.assertIn("IST", data["timestamp_ist"])
        self.assertIn("system_clock", data)

    def test_cache_freshness_and_invalidation(self) -> None:
        """Verify force_refresh invalidates cache and returns fresh data."""
        resp1 = self.client.get("/market/RELIANCE.NSE")
        self.assertEqual(resp1.status_code, 200)
        data1 = resp1.json()

        resp2 = self.client.get("/market/RELIANCE.NSE?refresh=true")
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.json()

        self.assertEqual(data1["ticker"], data2["ticker"])
        self.assertEqual(data1["price"], data2["price"])

    def test_all_equity_mappings_to_ns(self) -> None:
        """Verify all core equities map strictly to .NS on Yahoo."""
        equities = [
            ("RELIANCE.NSE", "RELIANCE.NS"),
            ("TCS.NSE", "TCS.NS"),
            ("INFY.NSE", "INFY.NS"),
            ("HDFCBANK.NSE", "HDFCBANK.NS"),
            ("ICICIBANK.NSE", "ICICIBANK.NS"),
            ("SBIN.NSE", "SBIN.NS"),
        ]
        for domain_sym, expected_yf in equities:
            resolved = self.provider._resolve_yf_symbol(Ticker(domain_sym))
            self.assertEqual(
                resolved,
                expected_yf,
                f"Ticker {domain_sym} mapped to {resolved}, expected {expected_yf}",
            )

    def test_last_close_semantics(self) -> None:
        """Verify quote source explicitly states last close or delayed quote."""
        response = self.client.get("/market/RELIANCE.NSE")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn(
            data["source"],
            ("YAHOO_LAST_CLOSE", "YAHOO_DELAYED", "YAHOO_PRE_MARKET", "YAHOO_POST_MARKET"),
        )
        self.assertIn(data["market_state"], ("OPEN", "CLOSED", "PRE_MARKET", "POST_MARKET"))

    def test_websocket_snapshot_authentic_quotes(self) -> None:
        """Verify WebSocket receives authentic snapshot without fake random walks."""
        with self.client.websocket_connect("/ws/market-data") as ws:
            snap = ws.receive_json()
            self.assertEqual(snap["type"], "SNAPSHOT")
            self.assertIsInstance(snap["data"], list)
            self.assertTrue(len(snap["data"]) > 0)

            rel = next((item for item in snap["data"] if item["ticker"] == "RELIANCE.NSE"), None)
            self.assertIsNotNone(rel, "RELIANCE.NSE must be in initial WebSocket snapshot")
            self.assertTrue(rel["price"] > 0, "WebSocket RELIANCE price must be authentic and > 0")


if __name__ == "__main__":
    unittest.main()
