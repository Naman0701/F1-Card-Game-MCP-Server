"""Unit tests for src/services/power_service.py."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.power_service import (
    compute_base_power,
    compute_power,
    get_track_multiplier,
)


class TestComputeBasePower:
    @pytest.mark.asyncio
    async def test_returns_float(self, seeded_session: AsyncSession):
        result = await compute_base_power(seeded_session, driver_id=1)
        assert isinstance(result, float)

    @pytest.mark.asyncio
    async def test_positive_value(self, seeded_session: AsyncSession):
        result = await compute_base_power(seeded_session, driver_id=1)
        assert result > 0

    @pytest.mark.asyncio
    async def test_higher_id_higher_skills(self, seeded_session: AsyncSession):
        """Fixture seeds skills as 80+id+idx, so higher id → higher base_power."""
        power_1 = await compute_base_power(seeded_session, driver_id=1)
        power_5 = await compute_base_power(seeded_session, driver_id=5)
        assert power_5 > power_1

    @pytest.mark.asyncio
    async def test_nonexistent_driver_returns_zero(self, seeded_session: AsyncSession):
        result = await compute_base_power(seeded_session, driver_id=9999)
        assert result == 0.0


class TestGetTrackMultiplier:
    @pytest.mark.asyncio
    async def test_returns_float(self, seeded_session: AsyncSession):
        result = await get_track_multiplier(seeded_session, driver_id=1, track_id=1)
        assert isinstance(result, float)

    @pytest.mark.asyncio
    async def test_in_valid_range(self, seeded_session: AsyncSession):
        result = await get_track_multiplier(seeded_session, driver_id=1, track_id=1)
        assert 0.5 <= result <= 2.0

    @pytest.mark.asyncio
    async def test_default_when_missing(self, seeded_session: AsyncSession):
        result = await get_track_multiplier(
            seeded_session, driver_id=9999, track_id=9999
        )
        assert result == 1.0


class TestComputePower:
    @pytest.mark.asyncio
    async def test_equals_base_times_multiplier(self, seeded_session: AsyncSession):
        base = await compute_base_power(seeded_session, 1)
        mult = await get_track_multiplier(seeded_session, 1, 1)
        power = await compute_power(seeded_session, 1, 1)
        assert power == round(base * mult, 2)

    @pytest.mark.asyncio
    async def test_rounded_to_two_decimals(self, seeded_session: AsyncSession):
        power = await compute_power(seeded_session, 1, 1)
        assert power == round(power, 2)
