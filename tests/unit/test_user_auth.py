"""
Unit Tests for User Domain, Password Hashing, JWT Tokens, and Auth Application Service.
"""

import unittest

from packages.application.services.auth_application_service import AuthApplicationService
from packages.domain.enums.system import UserRole
from packages.domain.exceptions.business import (
    InvalidCredentialsError,
    PasswordValidationError,
    UserAlreadyExistsError,
)
from packages.domain.user.user import User
from packages.domain.value_objects.identifiers.uuid_wrappers import UserId
from packages.infrastructure.repositories.portfolio_repository import SQLPortfolioRepository
from packages.infrastructure.repositories.user_repository import SQLUserRepository
from packages.infrastructure.security.auth import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestUserDomainAndSecurity(unittest.TestCase):
    def test_user_creation_and_normalization(self):
        user = User(
            email="  TEST.USER@Domain.COM  ",
            password_hash="hashed",
            full_name="Test User",
            role=UserRole.USER,
        )
        self.assertEqual(user.email, "test.user@domain.com")
        self.assertEqual(user.full_name, "Test User")
        self.assertEqual(user.role, UserRole.USER)
        self.assertTrue(user.is_active)

    def test_password_strength_validation(self):
        # Valid password
        User.validate_password_strength("StrongPass123")

        # Too short
        with self.assertRaises(PasswordValidationError):
            User.validate_password_strength("Short1")

        # Missing uppercase
        with self.assertRaises(PasswordValidationError):
            User.validate_password_strength("lowercase123")

        # Missing digit
        with self.assertRaises(PasswordValidationError):
            User.validate_password_strength("NoDigitPass")

    def test_argon2id_hashing_and_verification(self):
        pwd = "MySecretPassword123"
        hashed = hash_password(pwd)
        self.assertTrue(hashed.startswith("$argon2id$"))
        self.assertTrue(verify_password(pwd, hashed))
        self.assertFalse(verify_password("WrongPassword123", hashed))

    def test_jwt_access_token_creation_and_decoding(self):
        uid = str(UserId.generate())
        token = create_access_token(user_id=uid, role="ADMIN")
        payload = decode_token(token)
        self.assertEqual(payload["sub"], uid)
        self.assertEqual(payload["role"], "ADMIN")
        self.assertEqual(payload["type"], "access")


class TestAuthApplicationService(unittest.TestCase):
    def setUp(self):
        self.user_repo = SQLUserRepository(session_factory=None)
        self.portfolio_repo = SQLPortfolioRepository(session_factory=None)
        self.service = AuthApplicationService(
            user_repository=self.user_repo,
            portfolio_repository=self.portfolio_repo,
        )

    def test_signup_creates_user_and_paper_portfolio(self):
        res = self.service.signup(
            email="trader@hedgefund.in",
            password="SecureTrader123",
            full_name="Alpha Trader",
        )
        self.assertEqual(res["email"], "trader@hedgefund.in")
        self.assertIsNotNone(res["paper_portfolio_id"])

        user = self.user_repo.get_by_email("trader@hedgefund.in")
        self.assertIsNotNone(user)
        assert user is not None
        assert user.paper_portfolio_id is not None

        portfolio = self.portfolio_repo.get_by_id(user.paper_portfolio_id)
        self.assertIsNotNone(portfolio)
        assert portfolio is not None
        self.assertEqual(portfolio.cash_balance.amount, 1000000.00)

    def test_signup_duplicate_email_raises_error(self):
        self.service.signup(
            email="dupe@hedgefund.in",
            password="SecurePassword123",
            full_name="First User",
        )
        with self.assertRaises(UserAlreadyExistsError):
            self.service.signup(
                email="dupe@hedgefund.in",
                password="AnotherPassword123",
                full_name="Second User",
            )

    def test_login_and_refresh_workflow(self):
        self.service.signup(
            email="login@hedgefund.in",
            password="AuthPassword123",
            full_name="Login User",
        )
        tokens = self.service.login("login@hedgefund.in", "AuthPassword123")
        self.assertIn("access_token", tokens)
        self.assertIn("refresh_token", tokens)

        # Invalid password
        with self.assertRaises(InvalidCredentialsError):
            self.service.login("login@hedgefund.in", "WrongPassword123")

        # Refresh token
        refreshed = self.service.refresh(tokens["refresh_token"])
        self.assertIn("access_token", refreshed)


if __name__ == "__main__":
    unittest.main()
