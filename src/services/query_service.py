"""Read-only query helpers: user hand, game status, leaderboard, and
shared detail loaders used across services.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.driver import Driver
from src.models.game import Game, GamePlayerHand, GameRound
from src.models.relations import DriverSkillRel
from src.models.track import Track
from src.models.user import User


async def get_user_hand(session: AsyncSession, game_id: int, user_id: int) -> dict:
    """Retrieve the user's remaining (unplayed) cards with skill details.

    Args:
        session: Active database session.
        game_id: ID of the game.
        user_id: ID of the human player.

    Returns:
        Dict with game_id, current round, current track, score,
        and a list of card dicts (driver_id, name, number, skills).
    """
    game = await session.get(Game, game_id)
    if not game:
        return {"error": f"Game {game_id} not found."}
    if game.user_id != user_id:
        return {"error": "This is not your game."}

    cards = await load_hand_details(session, game_id, user_id)

    current_round_row = await session.execute(
        select(GameRound).where(
            GameRound.game_id == game_id,
            GameRound.round_number == game.current_round,
        )
    )
    gr = current_round_row.scalar_one_or_none()
    track_name = None
    if gr:
        track = await session.get(Track, gr.track_id)
        track_name = track.name if track else None

    return {
        "game_id": game_id,
        "round": game.current_round,
        "current_track": track_name,
        "score": f"You {game.user_score} - {game.ai_score} AI",
        "cards": cards,
    }


async def get_status(session: AsyncSession, game_id: int) -> dict:
    """Get full game status including round-by-round history.

    Args:
        session: Active database session.
        game_id: ID of the game to inspect.

    Returns:
        Dict with game_id, status, current_round, score, and a
        rounds list where each entry shows the track, cards played,
        power scores, and winner (or "upcoming" for future rounds).
    """
    game = await session.execute(
        select(Game)
        .options(selectinload(Game.rounds).selectinload(GameRound.track))
        .options(selectinload(Game.rounds).selectinload(GameRound.user_driver))
        .options(selectinload(Game.rounds).selectinload(GameRound.ai_driver))
        .where(Game.id == game_id)
    )
    game = game.scalar_one_or_none()
    if not game:
        return {"error": f"Game {game_id} not found."}

    rounds_history = []
    for r in game.rounds:
        entry = {"round": r.round_number, "track": r.track.name}
        if r.winner:
            entry.update(
                {
                    "your_card": r.user_driver.name if r.user_driver else None,
                    "ai_card": r.ai_driver.name if r.ai_driver else None,
                    "your_power": r.user_power,
                    "ai_power": r.ai_power,
                    "winner": r.winner,
                }
            )
        else:
            entry["status"] = "upcoming"
        rounds_history.append(entry)

    return {
        "game_id": game_id,
        "status": game.status,
        "current_round": game.current_round,
        "score": f"You {game.user_score} - {game.ai_score} AI",
        "rounds": rounds_history,
    }


async def get_top_players(
    session: AsyncSession, top_n: int = 10, include_ai: bool = False
) -> list[dict]:
    """Fetch the leaderboard ranked by total points.

    Args:
        session: Active database session.
        top_n: Maximum number of players to return.
        include_ai: When True, include the AI opponent in results.

    Returns:
        List of dicts with rank, name, total_points, wins, losses,
        and games_played for each player.
    """
    query = select(User)
    if not include_ai:
        query = query.where(User.is_ai.is_(False))
    query = query.order_by(User.total_points.desc()).limit(top_n)
    result = await session.execute(query)
    return [
        {
            "rank": i,
            "name": u.name,
            "total_points": u.total_points,
            "wins": u.wins,
            "losses": u.losses,
            "games_played": u.games_played,
        }
        for i, u in enumerate(result.scalars().all(), start=1)
    ]


# ── Shared detail loaders ────────────────────────────────────────────────


async def load_hand_details(
    session: AsyncSession, game_id: int, user_id: int
) -> list[dict]:
    """Load unplayed cards with driver name, number, skills, and base_power.

    Args:
        session: Active database session.
        game_id: ID of the game.
        user_id: ID of the player whose hand to load.

    Returns:
        List of card dicts, each containing driver_id, name, number,
        skills dict, and base_power.
    """
    hands = await session.execute(
        select(GamePlayerHand)
        .options(
            selectinload(GamePlayerHand.driver)
            .selectinload(Driver.driver_skills)
            .selectinload(DriverSkillRel.skill)
        )
        .where(
            GamePlayerHand.game_id == game_id,
            GamePlayerHand.user_id == user_id,
            GamePlayerHand.is_played.is_(False),
        )
    )
    cards = []
    for h in hands.scalars().all():
        d = h.driver
        skills = {ds.skill.name: ds.value for ds in d.driver_skills}
        skill_values = list(skills.values())
        base_power = (
            round(sum(skill_values) / len(skill_values), 2) if skill_values else 0.0
        )
        cards.append(
            {
                "driver_id": d.id,
                "name": d.name,
                "number": d.number,
                "skills": skills,
                "base_power": base_power,
            }
        )
    return cards


async def load_track_details(session: AsyncSession, track_id: int) -> dict:
    """Load track metadata by ID.

    Args:
        session: Active database session.
        track_id: ID of the track to load.

    Returns:
        Dict with track_id, name, circuit_type, laps, and description.
    """
    track = await session.get(Track, track_id)
    return {
        "track_id": track.id,
        "name": track.name,
        "circuit_type": track.circuit_type,
        "laps": track.laps,
        "description": track.description,
    }
