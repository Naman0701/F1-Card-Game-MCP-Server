"""Functional / integration tests — full game flows end-to-end.

Tests exercise the service layer with a real in-memory DB,
simulating the same sequence of calls an MCP client would make.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.services.game_service import create_game, play_round
from src.services.query_service import get_status, get_top_players, get_user_hand


class TestFullGameFlow:
    """Play an entire 5-round game and verify every step."""

    @pytest.mark.asyncio
    async def test_complete_game(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        ai = (await s.execute(select(User).where(User.is_ai.is_(True)))).scalar_one()

        game_data = await create_game(s, human.id)
        assert "error" not in game_data
        game_id = game_data["game_id"]

        assert len(game_data["your_cards"]) == 5
        for card in game_data["your_cards"]:
            assert "driver_id" in card
            assert "name" in card
            assert "number" in card
            assert "skills" in card
            assert "base_power" in card
            assert len(card["skills"]) == 6

        assert "track" in game_data
        track = game_data["track"]
        assert "track_id" in track
        assert "name" in track
        assert "circuit_type" in track
        assert "description" in track

        results = []
        for i, card in enumerate(game_data["your_cards"]):
            result = await play_round(s, game_id, human.id, card["driver_id"])
            assert "error" not in result
            assert result["round"] == i + 1

            assert "your_base_power" in result
            assert "your_track_multiplier" in result
            assert "your_power" in result
            assert "ai_base_power" in result
            assert "ai_track_multiplier" in result
            assert "ai_power" in result

            expected_user_power = round(
                result["your_base_power"] * result["your_track_multiplier"], 2
            )
            assert result["your_power"] == expected_user_power
            expected_ai_power = round(
                result["ai_base_power"] * result["ai_track_multiplier"], 2
            )
            assert result["ai_power"] == expected_ai_power

            assert result["round_winner"] in ("user", "ai", "draw")

            if i < 4:
                assert "next_track" in result
                nt = result["next_track"]
                assert isinstance(nt, dict)
                assert "track_id" in nt
                assert "description" in nt
                assert "remaining_cards" in result
                assert len(result["remaining_cards"]) == 4 - i
            else:
                assert "game_over" in result

            results.append(result)

        go = results[-1]["game_over"]
        assert "result" in go
        assert "final_score" in go
        assert "your_rounds_won" in go
        assert "ai_rounds_won" in go
        assert "your_points_earned" in go
        assert "ai_points_earned" in go
        assert "your_total_points" in go

        user_rw = go["your_rounds_won"]
        ai_rw = go["ai_rounds_won"]
        if "You win" in go["result"]:
            assert go["your_points_earned"] == (2 * user_rw) + 5
            assert go["ai_points_earned"] == (2 * ai_rw) - 5
        elif "AI wins" in go["result"]:
            assert go["your_points_earned"] == (2 * user_rw) - 5
            assert go["ai_points_earned"] == (2 * ai_rw) + 5
        else:
            assert go["your_points_earned"] == 2 * user_rw
            assert go["ai_points_earned"] == 2 * ai_rw

        await s.refresh(human)
        await s.refresh(ai)
        assert human.games_played == 1
        assert ai.games_played == 1


class TestMultipleGames:
    """Verify a player can play back-to-back games and points accumulate."""

    @pytest.mark.asyncio
    async def test_second_game_after_completion(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()

        game1 = await create_game(s, human.id)
        for card in game1["your_cards"]:
            await play_round(s, game1["game_id"], human.id, card["driver_id"])

        game2 = await create_game(s, human.id)
        assert "error" not in game2
        assert game2["game_id"] != game1["game_id"]

    @pytest.mark.asyncio
    async def test_points_accumulate(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()

        for _ in range(2):
            game = await create_game(s, human.id)
            for card in game["your_cards"]:
                await play_round(s, game["game_id"], human.id, card["driver_id"])

        await s.refresh(human)
        assert human.games_played == 2


class TestStatusDuringGame:
    """Verify get_status and get_user_hand at various stages."""

    @pytest.mark.asyncio
    async def test_status_mid_game(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        game_data = await create_game(s, human.id)
        game_id = game_data["game_id"]

        driver_id = game_data["your_cards"][0]["driver_id"]
        await play_round(s, game_id, human.id, driver_id)

        status = await get_status(s, game_id)
        assert status["status"] == "in_progress"
        assert status["current_round"] == 2

        played = [r for r in status["rounds"] if "winner" in r]
        upcoming = [r for r in status["rounds"] if r.get("status") == "upcoming"]
        assert len(played) == 1
        assert len(upcoming) == 4

    @pytest.mark.asyncio
    async def test_hand_decreases_each_round(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        game_data = await create_game(s, human.id)
        game_id = game_data["game_id"]

        for i, card in enumerate(game_data["your_cards"][:3]):
            await play_round(s, game_id, human.id, card["driver_id"])
            hand = await get_user_hand(s, game_id, human.id)
            assert len(hand["cards"]) == 4 - i


class TestLeaderboard:
    @pytest.mark.asyncio
    async def test_leaderboard_after_game(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        game_data = await create_game(s, human.id)

        for card in game_data["your_cards"]:
            await play_round(s, game_data["game_id"], human.id, card["driver_id"])

        leaders = await get_top_players(s, top_n=10)
        assert len(leaders) >= 1
        assert leaders[0]["name"] == "TestPlayer"
        assert leaders[0]["games_played"] == 1

    @pytest.mark.asyncio
    async def test_leaderboard_excludes_ai(self, seeded_session: AsyncSession):
        leaders = await get_top_players(seeded_session, top_n=100)
        names = [entry["name"] for entry in leaders]
        assert "AI_Opponent" not in names


class TestEdgeCases:
    @pytest.mark.asyncio
    async def test_play_someone_elses_game(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        ai = (await s.execute(select(User).where(User.is_ai.is_(True)))).scalar_one()

        game_data = await create_game(s, human.id)
        result = await play_round(s, game_data["game_id"], ai.id, 1)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_get_hand_wrong_user(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        ai = (await s.execute(select(User).where(User.is_ai.is_(True)))).scalar_one()

        game_data = await create_game(s, human.id)
        result = await get_user_hand(s, game_data["game_id"], ai.id)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_status_nonexistent_game(self, seeded_session: AsyncSession):
        result = await get_status(seeded_session, 99999)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_play_card_completed_game(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        game_data = await create_game(s, human.id)

        for card in game_data["your_cards"]:
            await play_round(s, game_data["game_id"], human.id, card["driver_id"])

        result = await play_round(s, game_data["game_id"], human.id, 1)
        assert "error" in result
        assert "completed" in result["error"].lower()


class TestScoringFormulas:
    """Explicitly test each scoring scenario with controlled outcomes."""

    @pytest.mark.asyncio
    async def test_user_wins_all_rounds(self, seeded_session: AsyncSession):
        """If user wins all 5 rounds: user_pts = (2*5)+5 = 15, ai_pts = (2*0)-5 = -5."""
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        game_data = await create_game(s, human.id)

        with (
            patch("src.services.game_service.compute_base_power") as mock_bp,
            patch("src.services.game_service.get_track_multiplier") as mock_tm,
        ):

            async def fake_bp(session, driver_id):
                user_drivers = {c["driver_id"] for c in game_data["your_cards"]}
                return 100.0 if driver_id in user_drivers else 10.0

            async def fake_tm(session, driver_id, track_id):
                return 1.0

            mock_bp.side_effect = fake_bp
            mock_tm.side_effect = fake_tm

            last = None
            for card in game_data["your_cards"]:
                last = await play_round(
                    s, game_data["game_id"], human.id, card["driver_id"]
                )

        go = last["game_over"]
        assert go["result"] == "You win!"
        assert go["your_rounds_won"] == 5
        assert go["your_points_earned"] == 15
        assert go["ai_points_earned"] == -5

    @pytest.mark.asyncio
    async def test_ai_wins_all_rounds(self, seeded_session: AsyncSession):
        """If AI wins all 5 rounds: user_pts = (2*0)-5 = -5, ai_pts = (2*5)+5 = 15."""
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        game_data = await create_game(s, human.id)

        with (
            patch("src.services.game_service.compute_base_power") as mock_bp,
            patch("src.services.game_service.get_track_multiplier") as mock_tm,
        ):

            async def fake_bp(session, driver_id):
                user_drivers = {c["driver_id"] for c in game_data["your_cards"]}
                return 10.0 if driver_id in user_drivers else 100.0

            async def fake_tm(session, driver_id, track_id):
                return 1.0

            mock_bp.side_effect = fake_bp
            mock_tm.side_effect = fake_tm

            last = None
            for card in game_data["your_cards"]:
                last = await play_round(
                    s, game_data["game_id"], human.id, card["driver_id"]
                )

        go = last["game_over"]
        assert go["result"] == "AI wins!"
        assert go["ai_rounds_won"] == 5
        assert go["your_points_earned"] == -5
        assert go["ai_points_earned"] == 15

    @pytest.mark.asyncio
    async def test_draw_scenario(self, seeded_session: AsyncSession):
        """If all 5 rounds draw: each player has score=5 (5×1pt).

        rounds_won = score // 2 = 2 (integer division).
        Draw → user_pts = 2*2 = 4, ai_pts = 2*2 = 4.
        """
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        game_data = await create_game(s, human.id)

        with (
            patch("src.services.game_service.compute_base_power") as mock_bp,
            patch("src.services.game_service.get_track_multiplier") as mock_tm,
        ):

            async def fake_bp(session, driver_id):
                return 80.0

            async def fake_tm(session, driver_id, track_id):
                return 1.0

            mock_bp.side_effect = fake_bp
            mock_tm.side_effect = fake_tm

            last = None
            for card in game_data["your_cards"]:
                last = await play_round(
                    s, game_data["game_id"], human.id, card["driver_id"]
                )

        go = last["game_over"]
        assert go["result"] == "It's a draw!"
        assert go["your_rounds_won"] == 2
        assert go["ai_rounds_won"] == 2
        assert go["your_points_earned"] == 4
        assert go["ai_points_earned"] == 4
