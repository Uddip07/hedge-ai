"""
Unit & Integration Tests for n8n Automation & Orchestration API Endpoints.
"""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from packages.api.config import APIConfig
from packages.api.main import app
from packages.infrastructure.database.session import DatabaseManager

AUTH_HEADERS = {"X-API-Key": APIConfig().automation_api_key}


@pytest.fixture
def client() -> TestClient:
    """Fixture providing FastAPI test client."""
    db = DatabaseManager()
    db.create_all()
    return TestClient(app)


class TestN8NOrchestrationEndpoints:
    """Test suite covering all FastAPI endpoints orchestrated by n8n workflows."""

    def test_authentication_enforcement_missing_key(self, client: TestClient) -> None:
        """Test that endpoints without X-API-Key return 401 Unauthorized."""
        payload = {"symbols": ["RELIANCE"], "days": 5}
        resp = client.post("/api/v1/market-data/sync", json=payload)
        assert resp.status_code == 401

    def test_authentication_enforcement_invalid_key(self, client: TestClient) -> None:
        """Test that endpoints with wrong X-API-Key return 401 Unauthorized."""
        payload = {"symbols": ["RELIANCE"], "days": 5}
        resp = client.post(
            "/api/v1/market-data/sync",
            json=payload,
            headers={"X-API-Key": "wrong-secret-key"},
        )
        assert resp.status_code == 401

    def test_detailed_health_probe(self, client: TestClient) -> None:
        """Test GET /health/detailed returns actual system probe metrics."""
        resp = client.get("/health/detailed")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert "components" in data
        assert "database" in data["components"]
        assert data["components"]["database"]["status"] == "healthy"
        assert "yahoo_provider" in data["components"]

    def test_market_data_sync_endpoint(self, client: TestClient) -> None:
        """Test POST /api/v1/market-data/sync triggers ingestion into DB."""
        payload = {
            "symbols": ["RELIANCE"],
            "days": 5,
        }
        resp = client.post("/api/v1/market-data/sync", json=payload, headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "job_id" in data
        assert data["status"] in ("COMPLETED", "PARTIAL")
        assert data["symbols_requested"] == 1
        assert "RELIANCE" in data["synced_symbols"]

    def test_daily_market_summary_endpoint(self, client: TestClient) -> None:
        """Test GET /market/summary/daily produces structured closing summary."""
        resp = client.get("/market/summary/daily", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "report_date" in data
        assert "benchmarks" in data
        assert "sector_performance" in data
        assert "top_gainers" in data
        assert "top_losers" in data
        assert "market_breadth" in data

    def test_news_ingestion_and_deduplication(self, client: TestClient) -> None:
        """Test POST /market/news/ingest fetches and deduplicates news."""
        resp = client.post("/market/news/ingest", json=["RELIANCE"], headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "COMPLETED"
        assert "articles" in data
        assert isinstance(data["articles"], list)
        if data["articles"]:
            # Ensure no fake sentiment numbers
            for art in data["articles"]:
                assert "title" in art
                assert "url" in art
                assert "sentiment_score" in art
                assert "sentiment_label" in art

    def test_backtest_run_validation_failure(self, client: TestClient) -> None:
        """Test POST /api/v1/backtest/run rejects invalid date ranges."""
        payload = {
            "strategy_id": "MOMENTUM_SMA",
            "symbols": ["RELIANCE"],
            "start_date": "2025-01-01",
            "end_date": "2024-01-01",  # Invalid start >= end
            "initial_capital": 100000.0,
        }
        resp = client.post("/api/v1/backtest/run", json=payload, headers=AUTH_HEADERS)
        assert resp.status_code == 422

    def test_backtest_run_and_retrieve_flow(self, client: TestClient) -> None:
        """Test POST /api/v1/backtest/run executes and persists backtest."""
        # Sync a few days first to ensure prices exist in DB
        client.post(
            "/api/v1/market-data/sync",
            json={"symbols": ["RELIANCE"], "days": 30},
            headers=AUTH_HEADERS,
        )

        payload = {
            "strategy_id": "MOMENTUM_SMA",
            "symbols": ["RELIANCE"],
            "start_date": str(date(2025, 1, 1)),
            "end_date": str(date(2026, 8, 1)),
            "initial_capital": 500000.0,
            "parameters": {"sma_window": 5},
        }
        resp = client.post("/api/v1/backtest/run", json=payload, headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "run_id" in data
        run_id = data["run_id"]
        assert data["status"] == "COMPLETED"
        assert "final_portfolio_value" in data
        assert "total_return_pct" in data

        # Retrieve backtest details
        get_resp = client.get(f"/api/v1/backtest/{run_id}")
        assert get_resp.status_code == 200
        get_data = get_resp.json()
        assert get_data["run_id"] == run_id
        assert get_data["strategy_name"] == "MOMENTUM_SMA"

    def test_broker_health_monitor(self, client: TestClient) -> None:
        """Test GET /broker/health safely reports broker state."""
        resp = client.get("/broker/health", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert "is_authenticated" in data
        assert "orders_summary" in data
        assert "rejected_orders" in data["orders_summary"]

    def test_alert_dispatch_and_list(self, client: TestClient) -> None:
        """Test POST /api/v1/alerts/dispatch and GET /api/v1/alerts/recent."""
        payload = {
            "alert_type": "MARKET_DATA_FAILURE",
            "severity": "WARNING",
            "source": "test_suite",
            "title": "Test Alert Event",
            "message": "Testing alert logging and database recording",
            "metadata": {"test_key": "test_value"},
        }
        post_resp = client.post("/api/v1/alerts/dispatch", json=payload, headers=AUTH_HEADERS)
        assert post_resp.status_code == 200
        post_data = post_resp.json()
        assert post_data["status"] == "DISPATCHED"
        assert post_data["recorded"] is True

        # Fetch recent alerts
        get_resp = client.get("/api/v1/alerts/recent")
        assert get_resp.status_code == 200
        recent = get_resp.json()
        assert isinstance(recent, list)
        assert len(recent) > 0
        assert any(a.get("title") == "Test Alert Event" for a in recent)
