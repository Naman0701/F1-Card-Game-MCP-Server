"""Unit tests for src/services/query_service.py — read-only queries and loaders."""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.track import Track
from src.models.user import User
from src.services.game_service import create_game, play_round
from src.services.query_service import (
    get_status,
    get_top_players,
    get_user_hand,
    load_hand_details,
    load_track_details,
)


class TestGetUserHand:
    @pytest.mark.asyncio
    async def test_returns_cards_with_base_power(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        game_data = await create_game(s, human.id)

        result = await get_user_hand(s, game_data["game_id"], human.id)
        assert "cards" in result
        for card in result["cards"]:
            assert "base_power" in card
            assert "skills" in card

    @pytest.mark.asyncio
    async def test_wrong_user(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        ai = (await s.execute(select(User).where(User.is_ai.is_(True)))).scalar_one()
        game_data = await create_game(s, human.id)

        result = await get_user_hand(s, game_data["game_id"], ai.id)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_nonexistent_game(self, seeded_session: AsyncSession):
        result = await get_user_hand(seeded_session, 9999, 1)
        assert "error" in result


class TestGetStatus:
    @pytest.mark.asyncio
    async def test_shows_upcoming_rounds(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        game_data = await create_game(s, human.id)

        status = await get_status(s, game_data["game_id"])
        assert status["status"] == "in_progress"
        assert len(status["rounds"]) == 5
        for r in status["rounds"]:
            assert r.get("status") == "upcoming"

    @pytest.mark.asyncio
    async def test_shows_played_rounds(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        game_data = await create_game(s, human.id)

        driver_id = game_data["your_cards"][0]["driver_id"]
        await play_round(s, game_data["game_id"], human.id, driver_id)

        status = await get_status(s, game_data["game_id"])
        played = [r for r in status["rounds"] if "winner" in r]
        upcoming = [r for r in status["rounds"] if r.get("status") == "upcoming"]
        assert len(played) == 1
        assert len(upcoming) == 4

    @pytest.mark.asyncio
    async def test_nonexistent_game(self, seeded_session: AsyncSession):
        result = await get_status(seeded_session, 99999)
        assert "error" in result


class TestGetTopPlayers:
    @pytest.mark.asyncio
    async def test_excludes_ai(self, seeded_session: AsyncSession):
        result = await get_top_players(seeded_session)
        for entry in result:
            assert entry["name"] != "AI_Opponent"

    @pytest.mark.asyncio
    async def test_includes_ai_when_requested(self, seeded_session: AsyncSession):
        result = await get_top_players(seeded_session, include_ai=True)
        names = [entry["name"] for entry in result]
        assert "AI_Opponent" in names

    @pytest.mark.asyncio
    async def test_include_ai_false_by_default(self, seeded_session: AsyncSession):
        result = await get_top_players(seeded_session)
        names = [entry["name"] for entry in result]
        assert "AI_Opponent" not in names

    @pytest.mark.asyncio
    async def test_respects_limit(self, seeded_session: AsyncSession):
        result = await get_top_players(seeded_session, top_n=1)
        assert len(result) <= 1

    @pytest.mark.asyncio
    async def test_result_fields(self, seeded_session: AsyncSession):
        result = await get_top_players(seeded_session)
        for entry in result:
            assert "rank" in entry
            assert "name" in entry
            assert "total_points" in entry
            assert "wins" in entry
            assert "losses" in entry
            assert "games_played" in entry

    @pytest.mark.asyncio
    async def test_ordered_by_points(self, seeded_session: AsyncSession):
        s = seeded_session
        u1 = User(name="high_scorer", total_points=100, is_ai=False)
        u2 = User(name="low_scorer", total_points=10, is_ai=False)
        s.add_all([u1, u2])
        await s.commit()

        result = await get_top_players(s)
        points = [entry["total_points"] for entry in result]
        assert points == sorted(points, reverse=True)


class TestLoadHandDetails:
    @pytest.mark.asyncio
    async def test_base_power_calculation(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        game_data = await create_game(s, human.id)

        cards = await load_hand_details(s, game_data["game_id"], human.id)
        for card in cards:
            skill_vals = list(card["skills"].values())
            expected_bp = round(sum(skill_vals) / len(skill_vals), 2)
            assert card["base_power"] == expected_bp


class TestLoadTrackDetails:
    @pytest.mark.asyncio
    async def test_includes_description(self, seeded_session: AsyncSession):
        s = seeded_session
        track = (await s.execute(select(Track))).scalars().first()
        result = await load_track_details(s, track.id)
        assert "description" in result
        assert result["description"] is not None
        assert "track_id" in result
        assert "name" in result
        assert "circuit_type" in result
        assert "laps" in result
