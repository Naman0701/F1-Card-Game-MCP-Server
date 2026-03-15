"""MCP tools for game lifecycle: starting games and playing cards."""

import json

from src.models.base import async_session
from src.models.game import Game
from src.services.game_service import create_game, play_round


def _fmt(data: dict | list) -> str:
    """Serialize a dict or list to a pretty-printed JSON string.

    Args:
        data: The data structure to serialize.

    Returns:
        JSON string with 2-space indentation.
    """
    return json.dumps(data, indent=2)


async def start_game(user_id: int) -> str:
    """Start a new F1 Card Game.

    Deals 5 random driver cards to you and 5 to the AI, selects
    5 random tracks for the rounds, and returns your hand plus
    the first track.

    Args:
        user_id: Your player ID (from the welcome tool).

    Returns:
        JSON with game_id, your cards (with skills), and round 1 track.
    """
    async with async_session() as session:
        async with session.begin():
            result = await create_game(session, user_id)
    return _fmt(result)


async def play_card(game_id: int, driver_id: int) -> str:
    """Play a driver card for the current round.

    The AI will also play a random card. Both power scores are
    computed and the round winner is determined. After round 5
    the game auto-finalizes with total point awards.

    Args:
        game_id: The ID of your active game.
        driver_id: The driver_id of the card you want to play.

    Returns:
        JSON with round result (cards, powers, winner, score) and
        next-round info or game_over summary.
    """
    async with async_session() as session:
        async with session.begin():
            game = await session.get(Game, game_id)
            if not game:
                return _fmt({"error": f"Game {game_id} not found."})
            result = await play_round(session, game_id, game.user_id, driver_id)
    return _fmt(result)
