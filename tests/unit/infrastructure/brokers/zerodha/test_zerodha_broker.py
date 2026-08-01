"""
Unit Tests for Official Zerodha KiteConnect Integration.

Validates FileTokenStore, ZerodhaAuthenticator, ZerodhaClient, ZerodhaBrokerAdapter,
portfolio, orders, and GTT managers by mocking the official kiteconnect SDK.
"""

from unittest.mock import MagicMock

import pytest

from packages.infrastructure.brokers.zerodha import (
    FileTokenStore,
    ZerodhaAuthenticator,
    ZerodhaBrokerAdapter,
    ZerodhaClient,
)


@pytest.fixture
def mock_kite():
    mock = MagicMock()
    mock.login_url.return_value = "https://kite.zerodha.com/connect/login?v=3&api_key=test_key"
    mock.generate_session.return_value = {
        "access_token": "test_access_token_123",
        "user_id": "AB1234",
        "user_name": "Test User",
        "email": "test@example.com",
    }
    mock.profile.return_value = {
        "user_id": "AB1234",
        "user_name": "Test User",
        "email": "test@example.com",
        "broker": "ZERODHA",
    }
    mock.holdings.return_value = [
        {
            "tradingsymbol": "RELIANCE",
            "exchange": "NSE",
            "quantity": 10,
            "average_price": 2400.0,
            "last_price": 2450.0,
            "pnl": 500.0,
        }
    ]
    mock.positions.return_value = {
        "net": [
            {
                "tradingsymbol": "INFY",
                "exchange": "NSE",
                "quantity": 5,
                "average_price": 1400.0,
                "last_price": 1420.0,
            }
        ],
        "day": [],
    }
    mock.margins.return_value = {
        "net": 100000.0,
        "available": {"cash": 75000.0, "collateral": 25000.0},
        "utilised": {"debits": 0.0},
    }
    mock.orders.return_value = [
        {
            "order_id": "240101001",
            "status": "COMPLETE",
            "tradingsymbol": "TCS",
            "transaction_type": "BUY",
            "quantity": 2,
            "price": 3500.0,
        }
    ]
    mock.place_order.return_value = "240101002"
    mock.modify_order.return_value = "240101002"
    mock.cancel_order.return_value = "240101002"
    mock.get_gtts.return_value = [
        {
            "id": 101,
            "user_id": "AB1234",
            "type": "single",
            "status": "active",
            "condition": {"tradingsymbol": "WIPRO"},
        }
    ]
    mock.place_gtt.return_value = {"trigger_id": 102}
    return mock


class TestFileTokenStore:
    def test_save_and_get_token(self, tmp_path):
        token_file = tmp_path / "zerodha_session.json"
        store = FileTokenStore(file_path=token_file)

        assert store.get_token() is None

        store.save_token("sample_token_xyz", metadata={"user_id": "U123"})
        assert store.get_token() == "sample_token_xyz"
        assert store.get_metadata().get("user_id") == "U123"

        store.clear_token()
        assert store.get_token() is None


class TestZerodhaAuthenticator:
    def test_get_login_url(self, mock_kite):
        auth = ZerodhaAuthenticator(api_key="test_key", api_secret="test_sec")
        auth.kite = mock_kite

        url = auth.get_login_url()
        assert "kite.zerodha.com" in url

    def test_generate_session(self, mock_kite, tmp_path):
        store = FileTokenStore(file_path=tmp_path / "session.json")
        auth = ZerodhaAuthenticator(api_key="test_key", api_secret="test_sec", token_store=store)
        auth.kite = mock_kite

        session_data = auth.generate_session("request_token_999")
        assert session_data["access_token"] == "test_access_token_123"
        assert store.get_token() == "test_access_token_123"


class TestZerodhaBrokerAdapter:
    def test_adapter_operations(self, mock_kite, tmp_path):
        store = FileTokenStore(file_path=tmp_path / "session.json")
        store.save_token("test_access_token_123")

        client = ZerodhaClient(
            api_key="test_key", access_token="test_access_token_123", kite_instance=mock_kite
        )
        adapter = ZerodhaBrokerAdapter(client=client)

        profile = adapter.profile()
        assert profile["user_id"] == "AB1234"

        holdings = adapter.holdings()
        assert len(holdings) == 1
        assert holdings[0]["tradingsymbol"] == "RELIANCE"

        positions = adapter.positions()
        assert len(positions["net"]) == 1

        funds = adapter.funds()
        assert funds["available_cash"] == 75000.0

        orders = adapter.orders()
        assert len(orders) == 1
        assert orders[0]["order_id"] == "240101001"

        order_res = adapter.place_order(
            {
                "tradingsymbol": "INFY",
                "transaction_type": "BUY",
                "quantity": 10,
                "price": 1400.0,
            }
        )
        assert order_res["order_id"] == "240101002"

        gtts = adapter.gtt()
        assert len(gtts) == 1
        assert gtts[0]["id"] == 101
