"""
Integration Tests for Authentication and User API Routers.
"""

import os
import unittest

from fastapi.testclient import TestClient

from packages.api.dependencies import get_container
from packages.api.main import create_app


class TestAuthAndUserAPIRouters(unittest.TestCase):
    def setUp(self):
        os.environ["IHF_RESET_STATE"] = "1"
        get_container.cache_clear()
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_auth_signup_login_profile_flow(self):
        # 1. Signup
        signup_resp = self.client.post(
            "/auth/signup",
            json={
                "email": "api.user@hedgefund.in",
                "password": "ApiUserPass123",
                "full_name": "API Tester",
            },
        )
        self.assertEqual(signup_resp.status_code, 201)
        self.assertIn("user", signup_resp.json())

        # 2. Login
        login_resp = self.client.post(
            "/auth/login",
            json={
                "email": "api.user@hedgefund.in",
                "password": "ApiUserPass123",
            },
        )
        self.assertEqual(login_resp.status_code, 200)
        data = login_resp.json()
        self.assertIn("access_token", data)
        token = data["access_token"]

        # 3. Access Protected Route /users/me
        headers = {"Authorization": f"Bearer {token}"}
        profile_resp = self.client.get("/users/me", headers=headers)
        self.assertEqual(profile_resp.status_code, 200)
        self.assertEqual(profile_resp.json()["email"], "api.user@hedgefund.in")

        # 4. Add to Watchlist
        watchlist_resp = self.client.post(
            "/users/me/watchlist",
            json={"symbol": "RELIANCE"},
            headers=headers,
        )
        self.assertEqual(watchlist_resp.status_code, 200)
        self.assertIn("RELIANCE", watchlist_resp.json()["watchlist"])

        # 5. Access without token fails
        unauth_resp = self.client.get("/users/me")
        self.assertEqual(unauth_resp.status_code, 401)
        self.assertEqual(unauth_resp.json()["error"]["code"], "UNAUTHORIZED")


if __name__ == "__main__":
    unittest.main()
