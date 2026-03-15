"""Power calculation: base power, track multiplier, and combined power score."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.constants import TRACK_MULTIPLIER_DEFAULT
from src.models.relations import DriverSkillRel, DriverTrackRel


async def compute_base_power(session: AsyncSession, driver_id: int) -> float:
    """Calculate a driver's base power (average of all 6 skill values).

    Args:
        session: Active database session.
        driver_id: ID of the driver to evaluate.

    Returns:
        Base power score rounded to 2 decimal places.
    """
    avg_result = await session.execute(
        select(func.avg(DriverSkillRel.value)).where(
            DriverSkillRel.driver_id == driver_id
        )
    )
    return round(float(avg_result.scalar() or 0.0), 2)


async def get_track_multiplier(
    session: AsyncSession, driver_id: int, track_id: int
) -> float:
    """Fetch the driver-track affinity multiplier.

    Args:
        session: Active database session.
        driver_id: ID of the driver.
        track_id: ID of the track.

    Returns:
        Multiplier (0.5–2.0), defaulting to 1.0 if no relation exists.
    """
    mult_result = await session.execute(
        select(DriverTrackRel.multiplier).where(
            DriverTrackRel.driver_id == driver_id,
            DriverTrackRel.track_id == track_id,
        )
    )
    return float(mult_result.scalar() or TRACK_MULTIPLIER_DEFAULT)


async def compute_power(session: AsyncSession, driver_id: int, track_id: int) -> float:
    """Calculate a driver's power score for a specific track.

    Formula: power = base_power × track multiplier.

    Args:
        session: Active database session.
        driver_id: ID of the driver to evaluate.
        track_id: ID of the track being raced.

    Returns:
        Power score rounded to 2 decimal places.
    """
    base = await compute_base_power(session, driver_id)
    mult = await get_track_multiplier(session, driver_id, track_id)
    return round(base * mult, 2)
