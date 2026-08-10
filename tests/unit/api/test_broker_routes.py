"""
Unit Tests for Broker API Routes (/auth/zerodha and /broker).

Validates OAuth endpoints, profile, holdings, positions, funds, order submission,
and GTT endpoints using FastAPI TestClient with mocked BrokerPort.
"""

from unittest.mock import MagicMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from packages.api.dependencies import get_broker_port
from packages.api.main import create_app


@pytest.fixture
def mock_broker_port():
    mock = MagicMock()
    mock.login.return_value = "https://kite.zerodha.com/connect/login?v=3&api_key=test_key"
    mock.profile.return_value = {
        "user_id": "TEST_USER",
        "user_name": "Test Trader",
        "email": "trader@example.com",
        "broker": "ZERODHA",
    }
    mock.holdings.return_value = [
        {"tradingsymbol": "RELIANCE", "quantity": 10, "last_price": 2450.0}
    ]
    mock.positions.return_value = {"net": [], "day": []}
    mock.funds.return_value = {"available_cash": 50000.0, "net": 50000.0}
    mock.orders.return_value = []
    mock.place_order.return_value = {"order_id": "999888", "status": "SUBMITTED"}
    mock.place_gtt.return_value = {"trigger_id": 777}
    return mock


@pytest.fixture
def client(mock_broker_port):
    app = create_app()
    app.dependency_overrides[get_broker_port] = lambda: mock_broker_port
    return TestClient(app)


class TestBrokerRoutes:
    def test_zerodha_login_route(self, client):
        from urllib.parse import urlparse

        res = client.get("/auth/zerodha/login", follow_redirects=False)
        assert res.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        location = res.headers.get("location", "")
        parsed = urlparse(location)
        assert parsed.hostname in ("kite.zerodha.com", "localhost", "127.0.0.1")

    def test_broker_profile_route(self, client):
        res = client.get("/broker/profile")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data["user_id"] == "TEST_USER"

    def test_broker_holdings_route(self, client):
        res = client.get("/broker/holdings")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert len(data) == 1
        assert data[0]["tradingsymbol"] == "RELIANCE"

    def test_broker_funds_route(self, client):
        res = client.get("/broker/funds")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data["available_cash"] == 50000.0

    def test_broker_place_order_route(self, client):
        payload = {
            "tradingsymbol": "INFY",
            "exchange": "NSE",
            "transaction_type": "BUY",
            "order_type": "LIMIT",
            "product": "CNC",
            "quantity": 5,
            "price": 1400.0,
        }
        res = client.post("/broker/order", json=payload)
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data["order_id"] == "999888"

    def test_broker_place_gtt_route(self, client):
        payload = {
            "trigger_type": "single",
            "tradingsymbol": "WIPRO",
            "exchange": "NSE",
            "trigger_values": [400.0],
            "last_price": 410.0,
            "orders": [
                {
                    "transaction_type": "SELL",
                    "quantity": 10,
                    "product": "CNC",
                    "order_type": "LIMIT",
                    "price": 400.0,
                }
            ],
        }
        res = client.post("/broker/gtt", json=payload)
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data["trigger_id"] == 777
