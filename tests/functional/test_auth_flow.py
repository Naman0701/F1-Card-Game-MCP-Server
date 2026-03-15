"""Functional tests — end-to-end auth flows exercising registration, login,
password management, and the full game lifecycle after authentication.

Monkeypatches ``async_session`` in tool modules to use the in-memory test DB.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from unittest.mock import patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.services.game_service import create_game, play_round
from src.services.query_service import get_top_players

TEST_KEY = b"functional-test-key"


def _mock_session_factory(real_session: AsyncSession):
    @asynccontextmanager
    async def _factory():
        yield real_session

    return _factory


class TestRegistrationAndLogin:
    """Full register → logout → login cycle."""

    @pytest.mark.asyncio
    async def test_register_logout_login(self, seeded_session: AsyncSession):
        s = seeded_session
        factory = _mock_session_factory(s)

        with (
            patch("src.tools.user_tools.async_session", factory),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import logout, welcome

            reg = await welcome("racer_one", "fast1234")
            assert "Welcome, racer_one" in reg
            assert "user_id" in reg

            uid = int(reg.split("user_id is ")[1].split(".")[0])

            lo = await logout(uid)
            assert "goodbye" in lo.lower()

            login = await welcome("racer_one", "fast1234")
            assert "Welcome back" in login

    @pytest.mark.asyncio
    async def test_register_case_variants(self, seeded_session: AsyncSession):
        """Registering 'Alice' and then logging in as 'alice' should work."""
        s = seeded_session
        factory = _mock_session_factory(s)

        with (
            patch("src.tools.user_tools.async_session", factory),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import welcome

            reg = await welcome("Alice", "pass1234")
            assert "Welcome," in reg

            login = await welcome("alice", "pass1234")
            assert "Welcome back" in login

            login_upper = await welcome("ALICE", "pass1234")
            assert "Welcome back" in login_upper


class TestPasswordManagement:
    """Flows around setting, changing, and recovering passwords."""

    @pytest.mark.asyncio
    async def test_legacy_user_sets_password_then_logs_in(
        self, seeded_session: AsyncSession
    ):
        """Pre-auth user with null password: set via update_password, then login."""
        s = seeded_session
        factory = _mock_session_factory(s)

        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        human.password_hash = None
        await s.commit()

        with (
            patch("src.tools.user_tools.async_session", factory),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import update_password, welcome

            attempt = await welcome("TestPlayer", "anything")
            assert "update_password" in attempt

            up = await update_password(human.id, "newpass1")
            assert "updated successfully" in up.lower()

            login = await welcome("TestPlayer", "newpass1")
            assert "Welcome back" in login

    @pytest.mark.asyncio
    async def test_change_password_full_cycle(self, seeded_session: AsyncSession):
        """Register → change password → old pass fails → new pass works."""
        s = seeded_session
        factory = _mock_session_factory(s)

        with (
            patch("src.tools.user_tools.async_session", factory),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import update_password, welcome

            reg = await welcome("changer", "old_pass1")
            uid = int(reg.split("user_id is ")[1].split(".")[0])

            up = await update_password(uid, "new_pass1", "old_pass1")
            assert "updated successfully" in up.lower()

            fail = await welcome("changer", "old_pass1")
            assert "Incorrect password" in fail

            ok = await welcome("changer", "new_pass1")
            assert "Welcome back" in ok


class TestAuthAndGameplay:
    """Register, play a game, verify leaderboard — the full experience."""

    @pytest.mark.asyncio
    async def test_register_play_game_leaderboard(self, seeded_session: AsyncSession):
        s = seeded_session
        factory = _mock_session_factory(s)

        with (
            patch("src.tools.user_tools.async_session", factory),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import welcome

            reg = await welcome("gamer_x", "play1234")
            uid = int(reg.split("user_id is ")[1].split(".")[0])

        game_data = await create_game(s, uid)
        assert "error" not in game_data

        for card in game_data["your_cards"]:
            await play_round(s, game_data["game_id"], uid, card["driver_id"])

        leaders = await get_top_players(s)
        names = [e["name"] for e in leaders]
        assert "gamer_x" in names

    @pytest.mark.asyncio
    async def test_leaderboard_ai_toggle(self, seeded_session: AsyncSession):
        """After a game, AI shows up only when include_ai=True."""
        s = seeded_session
        factory = _mock_session_factory(s)

        with (
            patch("src.tools.user_tools.async_session", factory),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import welcome

            reg = await welcome("leader_test", "pass1234")
            uid = int(reg.split("user_id is ")[1].split(".")[0])

        game_data = await create_game(s, uid)
        for card in game_data["your_cards"]:
            await play_round(s, game_data["game_id"], uid, card["driver_id"])

        without_ai = await get_top_players(s, include_ai=False)
        assert all(e["name"] != "AI_Opponent" for e in without_ai)

        with_ai = await get_top_players(s, include_ai=True)
        names = [e["name"] for e in with_ai]
        assert "AI_Opponent" in names


class TestEdgeCasesAuth:
    """Auth-specific edge cases."""

    @pytest.mark.asyncio
    async def test_duplicate_name_different_case(self, seeded_session: AsyncSession):
        """Trying to register a name that already exists (different case) should login, not duplicate."""
        s = seeded_session
        factory = _mock_session_factory(s)

        with (
            patch("src.tools.user_tools.async_session", factory),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import welcome

            await welcome("UniqueOne", "pass1234")
            result = await welcome("uniqueone", "pass1234")
            assert "Welcome back" in result

        users = (await s.execute(select(User).where(User.name == "uniqueone"))).scalars().all()
        assert len(users) == 1

    @pytest.mark.asyncio
    async def test_ai_login_blocked(self, seeded_session: AsyncSession):
        factory = _mock_session_factory(seeded_session)

        with (
            patch("src.tools.user_tools.async_session", factory),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import welcome

            result = await welcome("AI_Opponent", "hackme")
            assert "reserved" in result.lower()

    @pytest.mark.asyncio
    async def test_ai_logout_blocked(self, seeded_session: AsyncSession):
        s = seeded_session
        ai = (await s.execute(select(User).where(User.is_ai.is_(True)))).scalar_one()

        with patch("src.tools.user_tools.async_session", _mock_session_factory(s)):
            from src.tools.user_tools import logout

            result = await logout(ai.id)
            assert "cannot" in result.lower()

    @pytest.mark.asyncio
    async def test_ai_password_blocked(self, seeded_session: AsyncSession):
        s = seeded_session
        ai = (await s.execute(select(User).where(User.is_ai.is_(True)))).scalar_one()

        with (
            patch("src.tools.user_tools.async_session", _mock_session_factory(s)),
            patch("src.tools.user_tools._AUTH_KEY", TEST_KEY),
        ):
            from src.tools.user_tools import update_password

            result = await update_password(ai.id, "password")
            assert "ai" in result.lower()
