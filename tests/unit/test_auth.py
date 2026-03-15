"""Unit tests for password hashing and verification in src/tools/user_tools.py."""

from __future__ import annotations

from unittest.mock import patch

import hashlib
import hmac


TEST_KEY = b"test-secret-key"


def _make_hash(password: str) -> str:
    return hmac.new(TEST_KEY, password.encode(), hashlib.sha256).hexdigest()


class TestHashPassword:
    @patch("src.tools.user_tools._AUTH_KEY", TEST_KEY)
    def test_returns_hex_string(self):
        from src.tools.user_tools import _hash_password

        result = _hash_password("mypassword")
        assert isinstance(result, str)
        assert len(result) == 64  # SHA-256 hex digest

    @patch("src.tools.user_tools._AUTH_KEY", TEST_KEY)
    def test_deterministic(self):
        from src.tools.user_tools import _hash_password

        assert _hash_password("hello") == _hash_password("hello")

    @patch("src.tools.user_tools._AUTH_KEY", TEST_KEY)
    def test_different_passwords_produce_different_hashes(self):
        from src.tools.user_tools import _hash_password

        assert _hash_password("alpha") != _hash_password("bravo")

    @patch("src.tools.user_tools._AUTH_KEY", TEST_KEY)
    def test_matches_expected_hmac(self):
        from src.tools.user_tools import _hash_password

        expected = _make_hash("test123")
        assert _hash_password("test123") == expected


class TestVerifyPassword:
    @patch("src.tools.user_tools._AUTH_KEY", TEST_KEY)
    def test_correct_password(self):
        from src.tools.user_tools import _hash_password, _verify_password

        stored = _hash_password("secret")
        assert _verify_password("secret", stored) is True

    @patch("src.tools.user_tools._AUTH_KEY", TEST_KEY)
    def test_wrong_password(self):
        from src.tools.user_tools import _hash_password, _verify_password

        stored = _hash_password("secret")
        assert _verify_password("wrong", stored) is False

    @patch("src.tools.user_tools._AUTH_KEY", TEST_KEY)
    def test_case_sensitive(self):
        from src.tools.user_tools import _hash_password, _verify_password

        stored = _hash_password("Secret")
        assert _verify_password("secret", stored) is False
        assert _verify_password("Secret", stored) is True
