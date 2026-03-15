"""
Database seeding orchestrator.

Calls fetch_service to gather enriched data, then inserts rows into every
table in the correct dependency order. Safe to re-run — skips existing records.
"""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import async_session
from src.models.country import Country
from src.models.driver import Driver
from src.models.game import (
    Game,
    GamePlayerHand,
    GameRound,
)  # noqa: F401 – ensure tables registered
from src.models.relations import DriverSkillRel, DriverTrackRel, TeamDriverRel
from src.models.skill import Skill
from src.models.team import Team
from src.models.track import Track
from src.models.user import User
from src.services.fetch_service import (
    compute_all_driver_skills,
    compute_all_track_multipliers,
    fetch_countries,
    fetch_drivers,
    fetch_skills,
    fetch_teams,
    fetch_tracks,
)

logger = logging.getLogger(__name__)


async def seed_all() -> None:
    """Run every seed step inside a single session / transaction.

    Calls individual seed functions in dependency order:
    countries → skills → teams → drivers → tracks → relations → AI user.
    """
    async with async_session() as session:
        async with session.begin():
            country_ids = await seed_countries(session)
            skill_ids = await seed_skills(session)
            team_ids = await seed_teams(session, country_ids)
            driver_ids = await seed_drivers(session, country_ids)
            track_ids = await seed_tracks(session, country_ids)
            await seed_team_driver_relations(session, team_ids, driver_ids)
            await seed_driver_skills(session, driver_ids, skill_ids)
            await seed_driver_track_relations(session, driver_ids, track_ids)
            await seed_ai_user(session)
    logger.info("Seeding complete.")


# ── Individual seed functions ─────────────────────────────────────────────


async def seed_countries(session: AsyncSession) -> dict[str, int]:
    """Insert all countries from the constants data.

    Args:
        session: Active database session.

    Returns:
        Mapping of country name to database ID.
    """
    countries = fetch_countries()
    id_map: dict[str, int] = {}

    for name, code in countries.items():
        existing = (
            await session.execute(select(Country).where(Country.name == name))
        ).scalar_one_or_none()
        if existing:
            id_map[name] = existing.id
            continue
        obj = Country(name=name, code=code)
        session.add(obj)
        await session.flush()
        id_map[name] = obj.id

    logger.info("Seeded %d countries", len(id_map))
    return id_map


async def seed_skills(session: AsyncSession) -> dict[str, int]:
    """Insert the 6 skill definitions.

    Args:
        session: Active database session.

    Returns:
        Mapping of skill name to database ID.
    """
    skills = fetch_skills()
    id_map: dict[str, int] = {}

    for name, description in skills:
        existing = (
            await session.execute(select(Skill).where(Skill.name == name))
        ).scalar_one_or_none()
        if existing:
            id_map[name] = existing.id
            continue
        obj = Skill(name=name, description=description)
        session.add(obj)
        await session.flush()
        id_map[name] = obj.id

    logger.info("Seeded %d skills", len(id_map))
    return id_map


async def seed_teams(
    session: AsyncSession, country_ids: dict[str, int]
) -> dict[str, int]:
    """Insert all F1 teams.

    Args:
        session: Active database session.
        country_ids: Mapping of country name to ID for FK resolution.

    Returns:
        Mapping of team name to database ID.
    """
    teams = fetch_teams()
    id_map: dict[str, int] = {}

    for name, country_name in teams.items():
        existing = (
            await session.execute(select(Team).where(Team.name == name))
        ).scalar_one_or_none()
        if existing:
            id_map[name] = existing.id
            continue
        obj = Team(name=name, country_id=country_ids[country_name])
        session.add(obj)
        await session.flush()
        id_map[name] = obj.id

    logger.info("Seeded %d teams", len(id_map))
    return id_map


async def seed_drivers(
    session: AsyncSession, country_ids: dict[str, int]
) -> dict[str, int]:
    """Insert all 59 drivers with explicit serial primary keys.

    Args:
        session: Active database session.
        country_ids: Mapping of country name to ID for FK resolution.

    Returns:
        Mapping of driver name to database ID.
    """
    drivers = fetch_drivers()
    id_map: dict[str, int] = {}

    for drv in drivers:
        name = drv["name"]
        driver_id = drv["id"]
        existing = (
            await session.execute(select(Driver).where(Driver.id == driver_id))
        ).scalar_one_or_none()
        if existing:
            id_map[name] = existing.id
            continue
        obj = Driver(
            id=driver_id,
            name=name,
            number=drv["number"],
            country_id=country_ids[drv["country"]],
        )
        session.add(obj)
        await session.flush()
        id_map[name] = obj.id

    logger.info("Seeded %d drivers", len(id_map))
    return id_map


async def seed_tracks(
    session: AsyncSession, country_ids: dict[str, int]
) -> dict[str, int]:
    """Insert all 36 tracks.

    Args:
        session: Active database session.
        country_ids: Mapping of country name to ID for FK resolution.

    Returns:
        Mapping of track name to database ID.
    """
    tracks = fetch_tracks()
    id_map: dict[str, int] = {}

    for trk in tracks:
        name = trk["name"]
        existing = (
            await session.execute(select(Track).where(Track.name == name))
        ).scalar_one_or_none()
        if existing:
            if trk.get("description") and existing.description != trk["description"]:
                existing.description = trk["description"]
            id_map[name] = existing.id
            continue
        obj = Track(
            name=name,
            country_id=country_ids[trk["country"]],
            laps=trk["laps"],
            circuit_type=trk["circuit_type"],
            description=trk.get("description"),
        )
        session.add(obj)
        await session.flush()
        id_map[name] = obj.id

    logger.info("Seeded %d tracks", len(id_map))
    return id_map


async def seed_team_driver_relations(
    session: AsyncSession,
    team_ids: dict[str, int],
    driver_ids: dict[str, int],
) -> None:
    """Link each driver to their iconic/current team for a given season.

    Args:
        session: Active database session.
        team_ids: Mapping of team name to ID.
        driver_ids: Mapping of driver name to ID.
    """
    drivers = fetch_drivers()

    for drv in drivers:
        name = drv["name"]
        team_name = drv["team"]
        season_year = drv["peak_year"]

        driver_id = driver_ids[name]
        team_id = team_ids[team_name]

        exists = (
            await session.execute(
                select(TeamDriverRel).where(
                    TeamDriverRel.driver_id == driver_id,
                    TeamDriverRel.team_id == team_id,
                    TeamDriverRel.season_year == season_year,
                )
            )
        ).scalar_one_or_none()
        if exists:
            continue

        session.add(
            TeamDriverRel(team_id=team_id, driver_id=driver_id, season_year=season_year)
        )

    await session.flush()
    logger.info("Seeded team-driver relations")


async def seed_driver_skills(
    session: AsyncSession,
    driver_ids: dict[str, int],
    skill_ids: dict[str, int],
) -> None:
    """Compute and insert skill values for every driver × skill pair.

    Uses curated profiles for top-20 drivers and an algorithmic
    approach for the remaining 39.

    Args:
        session: Active database session.
        driver_ids: Mapping of driver name to ID.
        skill_ids: Mapping of skill name to ID.
    """
    all_skills = compute_all_driver_skills()

    for driver_name, skills in all_skills.items():
        driver_id = driver_ids[driver_name]
        for skill_name, value in skills.items():
            skill_id = skill_ids[skill_name]

            exists = (
                await session.execute(
                    select(DriverSkillRel).where(
                        DriverSkillRel.driver_id == driver_id,
                        DriverSkillRel.skill_id == skill_id,
                    )
                )
            ).scalar_one_or_none()
            if exists:
                continue

            session.add(
                DriverSkillRel(driver_id=driver_id, skill_id=skill_id, value=value)
            )

    await session.flush()
    logger.info("Seeded driver skills")


async def seed_driver_track_relations(
    session: AsyncSession,
    driver_ids: dict[str, int],
    track_ids: dict[str, int],
) -> None:
    """Compute and insert track multipliers for every driver × track pair.

    Multipliers range from 0.5 to 2.0 and are deterministically
    generated from driver/track name hashes.

    Args:
        session: Active database session.
        driver_ids: Mapping of driver name to ID.
        track_ids: Mapping of track name to ID.
    """
    multipliers = compute_all_track_multipliers()

    for driver_name, track_name, multiplier in multipliers:
        driver_id = driver_ids[driver_name]
        track_id = track_ids[track_name]

        existing = (
            await session.execute(
                select(DriverTrackRel).where(
                    DriverTrackRel.driver_id == driver_id,
                    DriverTrackRel.track_id == track_id,
                )
            )
        ).scalar_one_or_none()
        if existing:
            existing.multiplier = multiplier
        else:
            session.add(
                DriverTrackRel(
                    driver_id=driver_id, track_id=track_id, multiplier=multiplier
                )
            )

    await session.flush()
    logger.info("Seeded driver-track multipliers")


async def seed_ai_user(session: AsyncSession) -> int:
    """Ensure the persistent AI player exists in the users table.

    Args:
        session: Active database session.

    Returns:
        The AI user's database ID.
    """
    existing = (
        await session.execute(select(User).where(User.is_ai.is_(True)))
    ).scalar_one_or_none()
    if existing:
        logger.info("AI user already exists (id=%d)", existing.id)
        return existing.id

    ai = User(name="AI Opponent", is_ai=True)
    session.add(ai)
    await session.flush()
    logger.info("Created AI user (id=%d)", ai.id)
    return ai.id


# ── CLI entry point ───────────────────────────────────────────────────────

if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO, format="%(levelname)-5s %(message)s")
    asyncio.run(seed_all())
