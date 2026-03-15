"""MCP resources: read-only reference data for the F1 Card Game."""

import json

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.data.constants import (
    CARDS_PER_PLAYER,
    POINTS_GAME_LOSS_PENALTY,
    POINTS_GAME_WIN_BONUS,
    POINTS_PER_ROUND_DRAW,
    POINTS_PER_ROUND_WIN,
    ROUNDS_PER_GAME,
    SKILLS,
    TRACK_MULTIPLIER_DEFAULT,
    TRACK_MULTIPLIER_MAX,
    TRACK_MULTIPLIER_MIN,
)
from src.models.base import async_session
from src.models.driver import Driver
from src.models.relations import DriverSkillRel, TeamDriverRel
from src.models.track import Track


def get_rules() -> str:
    """Complete rules and scoring guide for the F1 Card Game."""
    return f"""\
# F1 Card Game — Rules

## Overview
Two players (you vs. AI) each receive {CARDS_PER_PLAYER} random F1 driver cards.
Over {ROUNDS_PER_GAME} rounds a track is revealed, both players play a card,
and the higher power score wins the round.

## Power Score
  power = average(all 6 skill values) × track_multiplier

Each driver has 6 skills rated 0–100. The track multiplier (per driver-track
pair) ranges from {TRACK_MULTIPLIER_MIN} to {TRACK_MULTIPLIER_MAX}, defaulting
to {TRACK_MULTIPLIER_DEFAULT} when no specific affinity exists.

## Round Scoring
- Round winner: +{POINTS_PER_ROUND_WIN} points to their game score
- Exact tie: +{POINTS_PER_ROUND_DRAW} point each

## Game End (after {ROUNDS_PER_GAME} rounds)
- Game winner: earns (2 × rounds_won) + {POINTS_GAME_WIN_BONUS} leaderboard points
- Game loser:  earns (2 × rounds_won) - {POINTS_GAME_LOSS_PENALTY} leaderboard points
- Draw: each earns (2 × rounds_won), no bonus or penalty

## Strategy Tips
- Check each driver's skills before playing — a high average doesn't always
  win if the track multiplier favours the opponent's driver.
- Street circuits tend to reward awareness and racecraft; high-speed circuits
  reward pace.
- The AI picks randomly, so smart card-track matching gives you an edge.

## Account Notes
- Usernames are case-insensitive.
- If you forget your password, contact NA (the admin) or register a new account.
"""


def get_skills() -> str:
    """Definitions of the 6 driver skills used in power calculation."""
    lines = ["# Driver Skills\n"]
    for name, description in SKILLS:
        lines.append(f"- **{name}**: {description}")
    lines.append(
        "\nA driver's base power is the average of all 6 skill values (0–100)."
    )
    return "\n".join(lines)


async def get_drivers() -> str:
    """Full catalog of all F1 drivers with their skills and team."""
    async with async_session() as session:
        result = await session.execute(
            select(Driver)
            .options(
                selectinload(Driver.country),
                selectinload(Driver.driver_skills).selectinload(DriverSkillRel.skill),
                selectinload(Driver.team_drivers).selectinload(TeamDriverRel.team),
            )
            .order_by(Driver.name)
        )
        drivers = []
        for d in result.scalars().all():
            skills = {ds.skill.name: ds.value for ds in d.driver_skills}
            teams = [
                {"team": td.team.name, "season": td.season_year}
                for td in d.team_drivers
            ]
            drivers.append(
                {
                    "driver_id": d.id,
                    "name": d.name,
                    "number": d.number,
                    "country": d.country.name,
                    "skills": skills,
                    "teams": teams,
                }
            )
    return json.dumps(drivers, indent=2)


async def get_tracks() -> str:
    """Full catalog of all tracks with circuit type and description."""
    async with async_session() as session:
        result = await session.execute(
            select(Track).options(selectinload(Track.country)).order_by(Track.name)
        )
        tracks = [
            {
                "track_id": t.id,
                "name": t.name,
                "country": t.country.name,
                "laps": t.laps,
                "circuit_type": t.circuit_type,
                "description": t.description,
            }
            for t in result.scalars().all()
        ]
    return json.dumps(tracks, indent=2)
