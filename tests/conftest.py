"""Shared fixtures for unit and functional tests.

Uses an in-memory SQLite database so tests run without Postgres.
Every test gets its own fresh database with all tables created.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.models.base import Base
from src.models.country import Country
from src.models.driver import Driver
from src.models.game import Game, GamePlayerHand, GameRound
from src.models.relations import DriverSkillRel, DriverTrackRel
from src.models.skill import Skill
from src.models.team import Team
from src.models.track import Track
from src.models.user import User

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def engine():
    eng = create_async_engine(TEST_DB_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def session(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as sess:
        yield sess


@pytest_asyncio.fixture
async def seeded_session(session: AsyncSession):
    """Session pre-loaded with minimal data needed for game tests.

    Creates: 1 country, 6 skills, 1 team, 10 drivers (with skills & track rels),
    5 tracks, 1 human user, 1 AI user.
    """
    country = Country(name="United Kingdom", code="GBR")
    session.add(country)
    await session.flush()

    skills = []
    for name, desc in [
        ("pace", "Raw single-lap speed"),
        ("racecraft", "Wheel-to-wheel racing ability"),
        ("awareness", "Spatial awareness"),
        ("experience", "Career experience"),
        ("wet_weather", "Rain performance"),
        ("tire_management", "Tire preservation"),
    ]:
        s = Skill(name=name, description=desc)
        session.add(s)
        skills.append(s)
    await session.flush()

    team = Team(name="TestTeam", country_id=country.id)
    session.add(team)
    await session.flush()

    drivers = []
    for i in range(1, 11):
        d = Driver(id=i, name=f"Driver_{i}", number=i, country_id=country.id)
        session.add(d)
        drivers.append(d)
    await session.flush()

    for d in drivers:
        for idx, s in enumerate(skills):
            value = 80 + d.id + idx
            if value > 100:
                value = 100
            session.add(DriverSkillRel(driver_id=d.id, skill_id=s.id, value=value))
    await session.flush()

    tracks = []
    for i in range(1, 6):
        t = Track(
            name=f"Track_{i}",
            country_id=country.id,
            laps=50 + i,
            circuit_type="technical",
            description=f"Description for Track_{i}",
        )
        session.add(t)
        tracks.append(t)
    await session.flush()

    for d in drivers:
        for t in tracks:
            mult = 0.8 + (d.id % 5) * 0.1 + (t.id % 3) * 0.15
            mult = round(min(2.0, max(0.5, mult)), 2)
            session.add(DriverTrackRel(driver_id=d.id, track_id=t.id, multiplier=mult))
    await session.flush()

    human = User(name="TestPlayer", is_ai=False)
    ai = User(name="AI_Opponent", is_ai=True)
    session.add(human)
    session.add(ai)
    await session.flush()

    await session.commit()
    yield session
