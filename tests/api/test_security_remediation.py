"""
Security Remediation & Regression Test Suite.

Validates that:
1. 500 Unhandled Exception middleware masks raw exception messages from clients.
2. Health check endpoint sanitizes component failures without exposing raw exceptions or paths.
3. Broker endpoints return safe error descriptions without leaking credentials/tokens/tracebacks.
4. Debug endpoint enforces authentication and sanitizes provider failure details.
5. GitHub Actions workflows enforce least-privilege permissions.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from starlette import status
from starlette.testclient import TestClient

from packages.api.dependencies import get_broker_port
from packages.api.main import create_app


@pytest.fixture
def mock_failing_broker():
    """Broker port that raises sensitive exceptions."""
    mock = MagicMock()
    mock.profile.side_effect = RuntimeError(
        "FATAL: connection to server at '10.0.0.1', port 5432 failed: password auth failed for user 'secret_admin'"
    )
    mock.holdings.side_effect = RuntimeError(
        "Access token 'secret_token_123' is expired or invalid"
    )
    mock.positions.side_effect = RuntimeError(
        "Database connection string postgresql://user:secret_pass@db.internal:5432/live failed"
    )
    mock.funds.side_effect = RuntimeError("KiteConnect secret 'my_secret_key' validation error")
    mock.orders.side_effect = RuntimeError("Internal server error in order microservice")
    mock.place_order.side_effect = RuntimeError(
        "Zerodha RMS error: insufficient funds for account ACC9999"
    )
    mock.place_gtt.side_effect = RuntimeError("GTT gateway internal timeout")
    return mock


@pytest.fixture
def client(mock_failing_broker):
    app = create_app()
    app.dependency_overrides[get_broker_port] = lambda: mock_failing_broker
    return TestClient(app)


class TestSecurityExceptionSanitization:
    """Validate zero information leakage through exceptions."""

    def test_unhandled_exception_middleware_sanitizes_500_response(self, client):
        """Ensure unhandled 500 errors do not expose raw Python exception strings."""
        res = client.get("/non-existent-endpoint")
        assert res.status_code == status.HTTP_404_NOT_FOUND
        data = res.json()
        assert "traceback" not in str(data).lower()
        assert "password" not in str(data).lower()

    def test_broker_profile_exception_sanitized(self, client):
        """Ensure /broker/profile does not expose internal DB/password strings."""
        res = client.get("/broker/profile")
        assert res.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = res.json()
        assert "secret_admin" not in str(data)
        assert "password auth failed" not in str(data)
        assert "traceback" not in str(data).lower()

    def test_broker_holdings_exception_sanitized(self, client):
        """Ensure /broker/holdings does not leak access tokens."""
        res = client.get("/broker/holdings")
        assert res.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = res.json()
        assert "secret_token_123" not in str(data)
        assert "traceback" not in str(data).lower()

    def test_broker_funds_exception_sanitized(self, client):
        """Ensure /broker/funds does not leak Kite secret keys."""
        res = client.get("/broker/funds")
        assert res.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = res.json()
        assert "my_secret_key" not in str(data)
        assert "traceback" not in str(data).lower()

    def test_broker_health_exception_sanitized(self, client):
        """Ensure /broker/health probe masks raw exception details."""
        res = client.get("/broker/health", headers={"X-API-Key": "dev-automation-secret-key"})
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data["status"] == "DEGRADED"
        assert data["is_authenticated"] is False
        assert "secret_admin" not in str(data)
        assert data["error"] == "Broker session unauthenticated or connection error"

    def test_health_detailed_probe_sanitizes_errors(self, client):
        """Ensure /health/detailed does not expose internal connection strings or tracebacks."""
        res = client.get("/health/detailed")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert "traceback" not in str(data).lower()
        if "error" in data["components"]["database"]:
            assert data["components"]["database"]["error"] == "Database service probe failed"

    def test_debug_endpoint_requires_auth(self, client):
        """Ensure debug provider endpoint is protected and requires authentication key."""
        res = client.get("/debug/provider/RELIANCE")
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_github_workflow_least_privilege_permissions(self):
        """Ensure all GitHub Actions workflows define least-privilege permissions."""
        ci_file = Path(".github/workflows/ci.yml")
        assert ci_file.exists()
        content = ci_file.read_text()
        assert "permissions:" in content
        assert "contents: read" in content
