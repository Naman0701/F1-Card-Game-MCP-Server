"""Unit tests for src/services/game_service.py — game lifecycle logic."""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.game import Game, GamePlayerHand
from src.models.user import User
from src.services.game_service import ai_select_card, create_game, play_round


class TestAiSelectCard:
    @pytest.mark.asyncio
    async def test_returns_valid_driver_id(self, seeded_session: AsyncSession):
        s = seeded_session
        users = (await s.execute(select(User))).scalars().all()
        human = next(u for u in users if not u.is_ai)
        ai = next(u for u in users if u.is_ai)

        game = Game(user_id=human.id, ai_user_id=ai.id)
        s.add(game)
        await s.flush()

        ai_driver_ids = [6, 7, 8, 9, 10]
        for did in ai_driver_ids:
            s.add(GamePlayerHand(game_id=game.id, user_id=ai.id, driver_id=did))
        await s.flush()

        selected = await ai_select_card(s, game.id, ai.id)
        assert selected in ai_driver_ids

    @pytest.mark.asyncio
    async def test_random_selection(self, seeded_session: AsyncSession):
        """Run multiple times — should not always pick the same card."""
        s = seeded_session
        users = (await s.execute(select(User))).scalars().all()
        human = next(u for u in users if not u.is_ai)
        ai = next(u for u in users if u.is_ai)

        game = Game(user_id=human.id, ai_user_id=ai.id)
        s.add(game)
        await s.flush()

        ai_driver_ids = [6, 7, 8, 9, 10]
        for did in ai_driver_ids:
            s.add(GamePlayerHand(game_id=game.id, user_id=ai.id, driver_id=did))
        await s.flush()

        selections = set()
        for _ in range(50):
            selected = await ai_select_card(s, game.id, ai.id)
            selections.add(selected)

        assert (
            len(selections) > 1
        ), "AI should select randomly, not always the same card"


class TestCreateGame:
    @pytest.mark.asyncio
    async def test_successful_creation(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        result = await create_game(s, human.id)

        assert "error" not in result
        assert "game_id" in result
        assert result["round"] == 1
        assert len(result["your_cards"]) == 5
        assert "track" in result

    @pytest.mark.asyncio
    async def test_cards_have_base_power(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        result = await create_game(s, human.id)

        for card in result["your_cards"]:
            assert "base_power" in card
            assert isinstance(card["base_power"], float)
            assert card["base_power"] > 0

    @pytest.mark.asyncio
    async def test_cards_have_skills(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        result = await create_game(s, human.id)

        for card in result["your_cards"]:
            assert "skills" in card
            assert len(card["skills"]) == 6

    @pytest.mark.asyncio
    async def test_track_has_description(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        result = await create_game(s, human.id)

        assert "description" in result["track"]
        assert result["track"]["description"] is not None

    @pytest.mark.asyncio
    async def test_no_overlapping_cards(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        result = await create_game(s, human.id)
        game_id = result["game_id"]

        hands = (
            (
                await s.execute(
                    select(GamePlayerHand).where(GamePlayerHand.game_id == game_id)
                )
            )
            .scalars()
            .all()
        )
        user_drivers = {h.driver_id for h in hands if h.user_id == human.id}
        ai_drivers = {h.driver_id for h in hands if h.user_id != human.id}
        assert user_drivers.isdisjoint(ai_drivers)

    @pytest.mark.asyncio
    async def test_nonexistent_user(self, seeded_session: AsyncSession):
        result = await create_game(seeded_session, 9999)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_ai_cannot_start(self, seeded_session: AsyncSession):
        s = seeded_session
        ai = (await s.execute(select(User).where(User.is_ai.is_(True)))).scalar_one()
        result = await create_game(s, ai.id)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_duplicate_active_game(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        await create_game(s, human.id)
        result2 = await create_game(s, human.id)
        assert "error" in result2
        assert "active game" in result2["error"].lower()


class TestPlayRound:
    async def _start_game(self, s: AsyncSession) -> dict:
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        return await create_game(s, human.id)

    @pytest.mark.asyncio
    async def test_round_result_structure(self, seeded_session: AsyncSession):
        s = seeded_session
        game_data = await self._start_game(s)
        driver_id = game_data["your_cards"][0]["driver_id"]
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()

        result = await play_round(s, game_data["game_id"], human.id, driver_id)

        assert "error" not in result
        assert result["round"] == 1
        assert "track" in result
        assert "your_card" in result
        assert "ai_card" in result
        assert result["round_winner"] in ("user", "ai", "draw")

    @pytest.mark.asyncio
    async def test_power_breakdown_fields(self, seeded_session: AsyncSession):
        s = seeded_session
        game_data = await self._start_game(s)
        driver_id = game_data["your_cards"][0]["driver_id"]
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()

        result = await play_round(s, game_data["game_id"], human.id, driver_id)

        assert "your_base_power" in result
        assert "your_track_multiplier" in result
        assert "your_power" in result
        assert "ai_base_power" in result
        assert "ai_track_multiplier" in result
        assert "ai_power" in result

    @pytest.mark.asyncio
    async def test_power_equals_base_times_multiplier(
        self, seeded_session: AsyncSession
    ):
        s = seeded_session
        game_data = await self._start_game(s)
        driver_id = game_data["your_cards"][0]["driver_id"]
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()

        result = await play_round(s, game_data["game_id"], human.id, driver_id)

        expected_user = round(
            result["your_base_power"] * result["your_track_multiplier"], 2
        )
        assert result["your_power"] == expected_user

        expected_ai = round(result["ai_base_power"] * result["ai_track_multiplier"], 2)
        assert result["ai_power"] == expected_ai

    @pytest.mark.asyncio
    async def test_next_track_has_full_details(self, seeded_session: AsyncSession):
        s = seeded_session
        game_data = await self._start_game(s)
        driver_id = game_data["your_cards"][0]["driver_id"]
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()

        result = await play_round(s, game_data["game_id"], human.id, driver_id)

        if "next_track" in result:
            nt = result["next_track"]
            assert "track_id" in nt
            assert "name" in nt
            assert "circuit_type" in nt
            assert "laps" in nt
            assert "description" in nt

    @pytest.mark.asyncio
    async def test_invalid_card(self, seeded_session: AsyncSession):
        s = seeded_session
        game_data = await self._start_game(s)
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()

        result = await play_round(s, game_data["game_id"], human.id, 9999)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_cannot_replay_card(self, seeded_session: AsyncSession):
        s = seeded_session
        game_data = await self._start_game(s)
        driver_id = game_data["your_cards"][0]["driver_id"]
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()

        await play_round(s, game_data["game_id"], human.id, driver_id)
        result2 = await play_round(s, game_data["game_id"], human.id, driver_id)
        assert "error" in result2

    @pytest.mark.asyncio
    async def test_wrong_game_id(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        result = await play_round(s, 9999, human.id, 1)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_score_increments(self, seeded_session: AsyncSession):
        s = seeded_session
        game_data = await self._start_game(s)
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()

        driver_id = game_data["your_cards"][0]["driver_id"]
        result = await play_round(s, game_data["game_id"], human.id, driver_id)

        score_parts = (
            result["score"].replace("You ", "").replace(" AI", "").split(" - ")
        )
        user_score = int(score_parts[0])
        ai_score = int(score_parts[1])

        if result["round_winner"] == "user":
            assert user_score == 2 and ai_score == 0
        elif result["round_winner"] == "ai":
            assert user_score == 0 and ai_score == 2
        else:
            assert user_score == 1 and ai_score == 1


class TestFinalizeGame:
    @pytest.mark.asyncio
    async def test_full_game_completes(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        game_data = await create_game(s, human.id)

        last_result = None
        for card in game_data["your_cards"]:
            last_result = await play_round(
                s, game_data["game_id"], human.id, card["driver_id"]
            )

        assert "game_over" in last_result

    @pytest.mark.asyncio
    async def test_game_status_completed(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        game_data = await create_game(s, human.id)

        for card in game_data["your_cards"]:
            await play_round(s, game_data["game_id"], human.id, card["driver_id"])

        game = await s.get(Game, game_data["game_id"])
        assert game.status == "completed"
        assert game.completed_at is not None

    @pytest.mark.asyncio
    async def test_scoring_formula(self, seeded_session: AsyncSession):
        """Verify: winner gets (2*rounds_won)+5, loser gets (2*rounds_won)-5."""
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        game_data = await create_game(s, human.id)

        last_result = None
        for card in game_data["your_cards"]:
            last_result = await play_round(
                s, game_data["game_id"], human.id, card["driver_id"]
            )

        go = last_result["game_over"]
        user_rw = go["your_rounds_won"]
        ai_rw = go["ai_rounds_won"]

        if "win" in go["result"].lower() and "ai" not in go["result"].lower():
            assert go["your_points_earned"] == (2 * user_rw) + 5
            assert go["ai_points_earned"] == (2 * ai_rw) - 5
        elif "ai wins" in go["result"].lower():
            assert go["your_points_earned"] == (2 * user_rw) - 5
            assert go["ai_points_earned"] == (2 * ai_rw) + 5
        else:
            assert go["your_points_earned"] == 2 * user_rw
            assert go["ai_points_earned"] == 2 * ai_rw

    @pytest.mark.asyncio
    async def test_stats_updated(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        game_data = await create_game(s, human.id)

        for card in game_data["your_cards"]:
            await play_round(s, game_data["game_id"], human.id, card["driver_id"])

        await s.refresh(human)
        assert human.games_played == 1
        assert human.wins + human.losses <= 1

    @pytest.mark.asyncio
    async def test_cannot_play_after_completion(self, seeded_session: AsyncSession):
        s = seeded_session
        human = (
            await s.execute(select(User).where(User.is_ai.is_(False)))
        ).scalar_one()
        game_data = await create_game(s, human.id)

        for card in game_data["your_cards"]:
            await play_round(s, game_data["game_id"], human.id, card["driver_id"])

        result = await play_round(s, game_data["game_id"], human.id, 1)
        assert "error" in result
