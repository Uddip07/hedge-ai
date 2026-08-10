"""
Unit Tests for Zerodha Infrastructure Services (Official KiteConnect SDK).

Validates authentication, order placement, portfolio normalization,
margins, GTT rules, and alert evaluation using official KiteConnect integration.
"""

from unittest.mock import MagicMock

import pytest

from packages.infrastructure.brokers.zerodha import (
    ZerodhaAlertService,
    ZerodhaAuthenticator,
    ZerodhaClient,
    ZerodhaGTTManager,
    ZerodhaMarginService,
    ZerodhaOrderManager,
    ZerodhaPortfolioManager,
)


@pytest.fixture
def mock_kite():
    mock = MagicMock()
    mock.login_url.return_value = "https://kite.zerodha.com/connect/login?v=3&api_key=my_key"
    mock.generate_session.return_value = {
        "access_token": "new_access_token_123",
        "user_id": "AB1234",
    }
    mock.profile.return_value = {"user_id": "AB1234", "user_name": "Trader"}
    mock.holdings.return_value = [
        {
            "tradingsymbol": "RELIANCE",
            "quantity": 10,
            "average_price": 2400.0,
            "last_price": 2450.0,
            "pnl": 500.0,
        }
    ]
    mock.margins.return_value = {
        "available": {"live_balance": 50000.0, "cash": 50000.0},
        "net": 50000.0,
    }
    mock.place_order.return_value = "240101001"
    mock.cancel_order.return_value = "240101001"
    mock.place_gtt.return_value = {"trigger_id": 101}
    return mock


@pytest.fixture
def zerodha_client(mock_kite):
    return ZerodhaClient(api_key="my_key", access_token="token_123", kite_instance=mock_kite)


class TestZerodhaAuthenticator:
    def test_get_login_url(self, mock_kite):
        from urllib.parse import parse_qs, urlparse

        auth = ZerodhaAuthenticator(api_key="my_key", api_secret="my_secret")
        auth.kite = mock_kite
        url = auth.get_login_url()

        parsed = urlparse(url)
        assert parsed.scheme in ("https", "http")
        assert parsed.hostname == "kite.zerodha.com"
        assert parsed.username is None
        query_params = parse_qs(parsed.query)
        assert query_params.get("api_key") == ["my_key"]

    def test_generate_session_success(self, mock_kite):
        auth = ZerodhaAuthenticator(api_key="my_key", api_secret="my_secret")
        auth.kite = mock_kite
        session = auth.generate_session("req_token_abc")
        assert session["access_token"] == "new_access_token_123"


class TestZerodhaOrderManager:
    def test_place_order_success(self, zerodha_client, mock_kite):
        mgr = ZerodhaOrderManager(zerodha_client)
        res = mgr.place_order(
            {
                "tradingsymbol": "RELIANCE",
                "transaction_type": "BUY",
                "quantity": 10,
                "price": 2400.0,
            }
        )
        assert res["order_id"] == "240101001"
        assert res["status"] == "SUBMITTED"

    def test_cancel_order(self, zerodha_client, mock_kite):
        mgr = ZerodhaOrderManager(zerodha_client)
        res = mgr.cancel_order(order_id="240101001")
        assert res["order_id"] == "240101001"
        assert res["status"] == "CANCELLED"


class TestZerodhaPortfolioManager:
    def test_get_holdings_normalization(self, zerodha_client, mock_kite):
        mgr = ZerodhaPortfolioManager(zerodha_client)
        holdings = mgr.get_holdings()
        assert len(holdings) == 1
        assert holdings[0]["tradingsymbol"] == "RELIANCE"
        assert holdings[0]["quantity"] == 10


class TestZerodhaMarginService:
    def test_equity_available_cash(self, zerodha_client, mock_kite):
        svc = ZerodhaMarginService(zerodha_client)
        cash = svc.get_equity_available_cash()
        assert cash == 50000.0


class TestZerodhaGTTManager:
    def test_create_gtt(self, zerodha_client, mock_kite):
        mgr = ZerodhaGTTManager(zerodha_client)
        res = mgr.place_gtt(
            {
                "trigger_type": "single",
                "tradingsymbol": "RELIANCE",
                "exchange": "NSE",
                "trigger_values": [2300.0],
                "last_price": 2400.0,
                "orders": [
                    {
                        "transaction_type": "BUY",
                        "quantity": 5,
                        "product": "CNC",
                        "order_type": "LIMIT",
                        "price": 2300.0,
                    }
                ],
            }
        )
        assert res["trigger_id"] == 101


class TestZerodhaAlertService:
    def test_alert_evaluation(self, zerodha_client, mock_kite):
        alert_svc = ZerodhaAlertService(zerodha_client)
        rule = alert_svc.create_alert(
            alert_id="ALT101",
            ticker_symbol="RELIANCE.NS",
            condition_type="GREATER_THAN",
            target_value=2450.0,
            message="Price exceeded target",
        )
        triggered = alert_svc.evaluate_price_trigger("RELIANCE.NS", 2500.0)
        assert len(triggered) == 1
        assert triggered[0].alert_id == "ALT101"
