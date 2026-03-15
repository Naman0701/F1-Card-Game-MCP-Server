"""Unit tests for src/tools/user_tools.py — welcome, update_password, logout, ensure_ai_user.

Each tool uses ``async_session`` internally, so we monkeypatch it to return
the test session (backed by in-memory SQLite).
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from unittest.mock import patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User

TEST_KEY = b"test-secret-key-for-tools"


def _mock_session_factory(real_session: AsyncSession):
    """Return a callable that mimics ``async_sessionmaker`` but yields *real_session*."""

    @asynccontextmanager
    async def _factory():
        yield real_session

    return _factory


# ── welcome ─────────────────────────────────────────────────────────────


class TestWelcome:
    @pytest.mark.asyncio
    async def test_register_new_user(self, seeded_session: AsyncSession):
        with (
            patch("src.tools.user_tools.async_session", _mock_session_factory(seeded_session)),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import welcome

            result = await welcome("newplayer", "pass1234")

        assert "Welcome, newplayer" in result
        assert "user_id" in result

    @pytest.mark.asyncio
    async def test_login_existing_user(self, seeded_session: AsyncSession):
        s = seeded_session
        from src.tools.user_tools import _hash_password

        with patch("src.tools.user_tools._AUTH_KEY", TEST_KEY):
            pw_hash = _hash_password("secret99")

        human = (await s.execute(select(User).where(User.is_ai.is_(False)))).scalar_one()
        human.password_hash = pw_hash
        await s.commit()

        with (
            patch("src.tools.user_tools.async_session", _mock_session_factory(s)),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import welcome

            result = await welcome("TestPlayer", "secret99")

        assert "Welcome back" in result
        assert str(human.id) in result

    @pytest.mark.asyncio
    async def test_wrong_password(self, seeded_session: AsyncSession):
        s = seeded_session
        from src.tools.user_tools import _hash_password

        with patch("src.tools.user_tools._AUTH_KEY", TEST_KEY):
            pw_hash = _hash_password("correct")

        human = (await s.execute(select(User).where(User.is_ai.is_(False)))).scalar_one()
        human.password_hash = pw_hash
        await s.commit()

        with (
            patch("src.tools.user_tools.async_session", _mock_session_factory(s)),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import welcome

            result = await welcome("TestPlayer", "wrong")

        assert "Incorrect password" in result

    @pytest.mark.asyncio
    async def test_case_insensitive_username(self, seeded_session: AsyncSession):
        s = seeded_session
        from src.tools.user_tools import _hash_password

        with patch("src.tools.user_tools._AUTH_KEY", TEST_KEY):
            pw_hash = _hash_password("mypass")

        human = (await s.execute(select(User).where(User.is_ai.is_(False)))).scalar_one()
        human.password_hash = pw_hash
        await s.commit()

        with (
            patch("src.tools.user_tools.async_session", _mock_session_factory(s)),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import welcome

            result = await welcome("testplayer", "mypass")

        assert "Welcome back" in result

    @pytest.mark.asyncio
    async def test_ai_account_blocked(self, seeded_session: AsyncSession):
        with (
            patch("src.tools.user_tools.async_session", _mock_session_factory(seeded_session)),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import welcome

            result = await welcome("AI_Opponent", "anypass")

        assert "reserved" in result.lower()

    @pytest.mark.asyncio
    async def test_null_password_account(self, seeded_session: AsyncSession):
        """Existing user with no password_hash should be asked to set one."""
        s = seeded_session
        human = (await s.execute(select(User).where(User.is_ai.is_(False)))).scalar_one()
        human.password_hash = None
        await s.commit()

        with (
            patch("src.tools.user_tools.async_session", _mock_session_factory(s)),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import welcome

            result = await welcome("TestPlayer", "anypass")

        assert "update_password" in result
        assert str(human.id) in result

    @pytest.mark.asyncio
    async def test_short_password_rejected(self, seeded_session: AsyncSession):
        with (
            patch("src.tools.user_tools.async_session", _mock_session_factory(seeded_session)),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import welcome

            result = await welcome("newguy", "ab")

        assert "at least 4" in result

    @pytest.mark.asyncio
    async def test_invalid_name_rejected(self, seeded_session: AsyncSession):
        with (
            patch("src.tools.user_tools.async_session", _mock_session_factory(seeded_session)),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import welcome

            result = await welcome("a", "password")  # too short

        assert "Invalid name" in result

    @pytest.mark.asyncio
    async def test_special_chars_name_rejected(self, seeded_session: AsyncSession):
        with (
            patch("src.tools.user_tools.async_session", _mock_session_factory(seeded_session)),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import welcome

            result = await welcome("bad name!", "password")

        assert "Invalid name" in result

    @pytest.mark.asyncio
    async def test_missing_auth_key(self, seeded_session: AsyncSession):
        with (
            patch("src.tools.user_tools.async_session", _mock_session_factory(seeded_session)),
            patch("src.tools.user_tools._AUTH_KEY", b""),
        ):
            from src.tools.user_tools import welcome

            result = await welcome("player", "password")

        assert "AUTH_SECRET_KEY" in result

    @pytest.mark.asyncio
    async def test_new_user_stored_lowercase(self, seeded_session: AsyncSession):
        s = seeded_session
        with (
            patch("src.tools.user_tools.async_session", _mock_session_factory(s)),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import welcome

            await welcome("MixedCase", "password1")

        user = (
            await s.execute(select(User).where(User.name == "mixedcase"))
        ).scalar_one_or_none()
        assert user is not None
        assert user.name == "mixedcase"


# ── update_password ─────────────────────────────────────────────────────


class TestUpdatePassword:
    @pytest.mark.asyncio
    async def test_set_password_on_null(self, seeded_session: AsyncSession):
        """Legacy user with no password can set one directly."""
        s = seeded_session
        human = (await s.execute(select(User).where(User.is_ai.is_(False)))).scalar_one()
        human.password_hash = None
        await s.commit()

        with (
            patch("src.tools.user_tools.async_session", _mock_session_factory(s)),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import update_password

            result = await update_password(human.id, "newpass1")

        assert "updated successfully" in result.lower()
        await s.refresh(human)
        assert human.password_hash is not None

    @pytest.mark.asyncio
    async def test_change_with_correct_current(self, seeded_session: AsyncSession):
        s = seeded_session
        from src.tools.user_tools import _hash_password

        with patch("src.tools.user_tools._AUTH_KEY", TEST_KEY):
            old_hash = _hash_password("oldpass")

        human = (await s.execute(select(User).where(User.is_ai.is_(False)))).scalar_one()
        human.password_hash = old_hash
        await s.commit()

        with (
            patch("src.tools.user_tools.async_session", _mock_session_factory(s)),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import update_password

            result = await update_password(human.id, "newpass1", "oldpass")

        assert "updated successfully" in result.lower()
        await s.refresh(human)
        assert human.password_hash != old_hash

    @pytest.mark.asyncio
    async def test_wrong_current_password(self, seeded_session: AsyncSession):
        s = seeded_session
        from src.tools.user_tools import _hash_password

        with patch("src.tools.user_tools._AUTH_KEY", TEST_KEY):
            old_hash = _hash_password("realpass")

        human = (await s.execute(select(User).where(User.is_ai.is_(False)))).scalar_one()
        human.password_hash = old_hash
        await s.commit()

        with (
            patch("src.tools.user_tools.async_session", _mock_session_factory(s)),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import update_password

            result = await update_password(human.id, "newpass1", "wrongpass")

        assert "incorrect" in result.lower()

    @pytest.mark.asyncio
    async def test_missing_current_when_set(self, seeded_session: AsyncSession):
        s = seeded_session
        from src.tools.user_tools import _hash_password

        with patch("src.tools.user_tools._AUTH_KEY", TEST_KEY):
            old_hash = _hash_password("existing")

        human = (await s.execute(select(User).where(User.is_ai.is_(False)))).scalar_one()
        human.password_hash = old_hash
        await s.commit()

        with (
            patch("src.tools.user_tools.async_session", _mock_session_factory(s)),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import update_password

            result = await update_password(human.id, "newpass1")

        assert "already have a password" in result.lower()

    @pytest.mark.asyncio
    async def test_short_new_password(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (await s.execute(select(User).where(User.is_ai.is_(False)))).scalar_one()

        with (
            patch("src.tools.user_tools.async_session", _mock_session_factory(s)),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import update_password

            result = await update_password(human.id, "ab")

        assert "at least 4" in result

    @pytest.mark.asyncio
    async def test_ai_cannot_update(self, seeded_session: AsyncSession):
        s = seeded_session
        ai = (await s.execute(select(User).where(User.is_ai.is_(True)))).scalar_one()

        with (
            patch("src.tools.user_tools.async_session", _mock_session_factory(s)),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import update_password

            result = await update_password(ai.id, "password")

        assert "ai" in result.lower()

    @pytest.mark.asyncio
    async def test_nonexistent_user(self, seeded_session: AsyncSession):
        with (
            patch("src.tools.user_tools.async_session", _mock_session_factory(seeded_session)),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import update_password

            result = await update_password(9999, "password")

        assert "no user" in result.lower()

    @pytest.mark.asyncio
    async def test_missing_auth_key(self, seeded_session: AsyncSession):
        with (
            patch("src.tools.user_tools.async_session", _mock_session_factory(seeded_session)),
            patch("src.tools.user_tools._AUTH_KEY", b""),
        ):
            from src.tools.user_tools import update_password

            result = await update_password(1, "password")

        assert "AUTH_SECRET_KEY" in result


# ── logout ──────────────────────────────────────────────────────────────


class TestLogout:
    @pytest.mark.asyncio
    async def test_successful_logout(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (await s.execute(select(User).where(User.is_ai.is_(False)))).scalar_one()

        with patch("src.tools.user_tools.async_session", _mock_session_factory(s)):
            from src.tools.user_tools import logout

            result = await logout(human.id)

        assert "goodbye" in result.lower()
        assert human.name in result

    @pytest.mark.asyncio
    async def test_ai_cannot_logout(self, seeded_session: AsyncSession):
        s = seeded_session
        ai = (await s.execute(select(User).where(User.is_ai.is_(True)))).scalar_one()

        with patch("src.tools.user_tools.async_session", _mock_session_factory(s)):
            from src.tools.user_tools import logout

            result = await logout(ai.id)

        assert "cannot" in result.lower()

    @pytest.mark.asyncio
    async def test_nonexistent_user(self, seeded_session: AsyncSession):
        with patch(
            "src.tools.user_tools.async_session",
            _mock_session_factory(seeded_session),
        ):
            from src.tools.user_tools import logout

            result = await logout(9999)

        assert "no user" in result.lower()


# ── ensure_ai_user ──────────────────────────────────────────────────────


class TestEnsureAiUser:
    @pytest.mark.asyncio
    async def test_already_exists(self, seeded_session: AsyncSession):
        with patch(
            "src.tools.user_tools.async_session",
            _mock_session_factory(seeded_session),
        ):
            from src.tools.user_tools import ensure_ai_user

            result = await ensure_ai_user()

        assert "already exists" in result.lower()

    @pytest.mark.asyncio
    async def test_creates_when_missing(self, seeded_session: AsyncSession):
        s = seeded_session
        ai = (await s.execute(select(User).where(User.is_ai.is_(True)))).scalar_one()
        await s.delete(ai)
        await s.commit()

        with patch("src.tools.user_tools.async_session", _mock_session_factory(s)):
            from src.tools.user_tools import ensure_ai_user

            result = await ensure_ai_user()

        assert "created" in result.lower()

        new_ai = (
            await s.execute(select(User).where(User.is_ai.is_(True)))
        ).scalar_one_or_none()
        assert new_ai is not None
        assert new_ai.name == "AI_Opponent"
