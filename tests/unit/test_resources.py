"""Unit tests for src/resources/game_resources.py — MCP resources."""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from unittest.mock import patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.resources.game_resources import get_rules, get_skills


def _mock_session_factory(real_session: AsyncSession):
    @asynccontextmanager
    async def _factory():
        yield real_session

    return _factory


class TestGetRules:
    def test_returns_string(self):
        result = get_rules()
        assert isinstance(result, str)

    def test_contains_key_sections(self):
        result = get_rules()
        assert "Overview" in result
        assert "Power Score" in result
        assert "Round Scoring" in result
        assert "Game End" in result
        assert "Strategy Tips" in result

    def test_contains_game_constants(self):
        result = get_rules()
        assert "5" in result  # CARDS_PER_PLAYER / ROUNDS_PER_GAME
        assert "0.5" in result  # TRACK_MULTIPLIER_MIN
        assert "2.0" in result  # TRACK_MULTIPLIER_MAX

    def test_mentions_case_insensitive_names(self):
        result = get_rules()
        assert "case-insensitive" in result.lower()


class TestGetSkills:
    def test_returns_string(self):
        result = get_skills()
        assert isinstance(result, str)

    def test_contains_all_six_skills(self):
        result = get_skills()
        for skill_name in [
            "pace",
            "racecraft",
            "awareness",
            "experience",
            "wet_weather",
            "tire_management",
        ]:
            assert skill_name in result

    def test_mentions_base_power_formula(self):
        result = get_skills()
        assert "average" in result.lower()


class TestGetDrivers:
    @pytest.mark.asyncio
    async def test_returns_json_list(self, seeded_session: AsyncSession):
        with patch(
            "src.resources.game_resources.async_session",
            _mock_session_factory(seeded_session),
        ):
            from src.resources.game_resources import get_drivers

            result = await get_drivers()

        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) == 10  # seeded 10 drivers

    @pytest.mark.asyncio
    async def test_driver_fields(self, seeded_session: AsyncSession):
        with patch(
            "src.resources.game_resources.async_session",
            _mock_session_factory(seeded_session),
        ):
            from src.resources.game_resources import get_drivers

            result = await get_drivers()

        data = json.loads(result)
        for driver in data:
            assert "driver_id" in driver
            assert "name" in driver
            assert "number" in driver
            assert "country" in driver
            assert "skills" in driver
            assert "teams" in driver

    @pytest.mark.asyncio
    async def test_drivers_sorted_by_name(self, seeded_session: AsyncSession):
        with patch(
            "src.resources.game_resources.async_session",
            _mock_session_factory(seeded_session),
        ):
            from src.resources.game_resources import get_drivers

            result = await get_drivers()

        data = json.loads(result)
        names = [d["name"] for d in data]
        assert names == sorted(names)


class TestGetTracks:
    @pytest.mark.asyncio
    async def test_returns_json_list(self, seeded_session: AsyncSession):
        with patch(
            "src.resources.game_resources.async_session",
            _mock_session_factory(seeded_session),
        ):
            from src.resources.game_resources import get_tracks

            result = await get_tracks()

        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) == 5  # seeded 5 tracks

    @pytest.mark.asyncio
    async def test_track_fields(self, seeded_session: AsyncSession):
        with patch(
            "src.resources.game_resources.async_session",
            _mock_session_factory(seeded_session),
        ):
            from src.resources.game_resources import get_tracks

            result = await get_tracks()

        data = json.loads(result)
        for track in data:
            assert "track_id" in track
            assert "name" in track
            assert "country" in track
            assert "laps" in track
            assert "circuit_type" in track
            assert "description" in track

    @pytest.mark.asyncio
    async def test_tracks_sorted_by_name(self, seeded_session: AsyncSession):
        with patch(
            "src.resources.game_resources.async_session",
            _mock_session_factory(seeded_session),
        ):
            from src.resources.game_resources import get_tracks

            result = await get_tracks()

        data = json.loads(result)
        names = [t["name"] for t in data]
        assert names == sorted(names)
