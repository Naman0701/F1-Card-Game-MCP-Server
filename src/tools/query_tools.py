"""MCP tools for read-only queries: hand inspection, game status, leaderboard."""

import json

from src.models.base import async_session
from src.models.game import Game
from src.services.query_service import get_status, get_top_players, get_user_hand


def _fmt(data: dict | list) -> str:
    """Serialize a dict or list to a pretty-printed JSON string.

    Args:
        data: The data structure to serialize.

    Returns:
        JSON string with 2-space indentation.
    """
    return json.dumps(data, indent=2)


async def get_hand(game_id: int) -> str:
    """View your remaining (unplayed) driver cards.

    Shows each card's skills, the current track, and the score
    so you can decide which card to play next.

    Args:
        game_id: The ID of your active game.

    Returns:
        JSON with remaining cards, current round, track, and score.
    """
    async with async_session() as session:
        game = await session.get(Game, game_id)
        if not game:
            return _fmt({"error": f"Game {game_id} not found."})
        result = await get_user_hand(session, game_id, game.user_id)
    return _fmt(result)


async def get_game_status(game_id: int) -> str:
    """View full game status with round-by-round history.

    Shows completed rounds (cards played, powers, winners) and
    upcoming rounds (track only).

    Args:
        game_id: The ID of the game to inspect.

    Returns:
        JSON with status, score, and per-round details.
    """
    async with async_session() as session:
        result = await get_status(session, game_id)
    return _fmt(result)


async def get_leaderboard(top_n: int = 10, include_ai: bool = False) -> str:
    """View the top players ranked by total points.

    By default only real players are shown. Set include_ai to True
    to include the AI opponent on the board.

    Args:
        top_n: Number of players to show (default 10).
        include_ai: Include the AI opponent in results (default False).

    Returns:
        JSON list of players with rank, name, points, wins, losses.
    """
    async with async_session() as session:
        result = await get_top_players(session, top_n, include_ai=include_ai)
    return _fmt(result)
