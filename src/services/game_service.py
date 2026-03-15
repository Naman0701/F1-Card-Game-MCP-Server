"""Game lifecycle: creating games, playing rounds, AI card selection,
and end-of-game scoring.
"""

from __future__ import annotations

import random
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.constants import (
    CARDS_PER_PLAYER,
    POINTS_GAME_LOSS_PENALTY,
    POINTS_GAME_WIN_BONUS,
    POINTS_PER_ROUND_DRAW,
    POINTS_PER_ROUND_WIN,
    ROUNDS_PER_GAME,
)
from src.models.driver import Driver
from src.models.game import Game, GamePlayerHand, GameRound
from src.models.track import Track
from src.models.user import User
from src.services.power_service import compute_base_power, get_track_multiplier
from src.services.query_service import load_hand_details, load_track_details

# ── AI card selection ─────────────────────────────────────────────────────


async def ai_select_card(session: AsyncSession, game_id: int, ai_user_id: int) -> int:
    """Select a random unplayed card from the AI's hand.

    The AI has no knowledge of the current track, making its
    selection fair and unpredictable.

    Args:
        session: Active database session.
        game_id: ID of the current game.
        ai_user_id: User ID of the AI opponent.

    Returns:
        Driver ID of the randomly selected card.
    """
    unplayed = await session.execute(
        select(GamePlayerHand.driver_id).where(
            GamePlayerHand.game_id == game_id,
            GamePlayerHand.user_id == ai_user_id,
            GamePlayerHand.is_played.is_(False),
        )
    )
    driver_ids = [row[0] for row in unplayed.all()]
    return random.choice(driver_ids)


# ── Start game ────────────────────────────────────────────────────────────


async def create_game(session: AsyncSession, user_id: int) -> dict:
    """Set up a new game by dealing cards and selecting tracks.

    Picks 10 random drivers (5 per player, no overlap) and 5 random
    tracks. Creates the Game, GamePlayerHand, and GameRound DB records.

    Args:
        session: Active database session (inside a transaction).
        user_id: ID of the human player starting the game.

    Returns:
        Dict with game_id, the user's cards, round 1 track info,
        or an error dict if validation fails.
    """
    user = await session.get(User, user_id)
    if not user:
        return {"error": f"User {user_id} not found."}
    if user.is_ai:
        return {"error": "AI user cannot start a game."}

    active = await session.execute(
        select(Game).where(Game.user_id == user_id, Game.status == "in_progress")
    )
    if active.scalar_one_or_none():
        return {"error": "You already have an active game. Finish or abandon it first."}

    ai_result = await session.execute(select(User).where(User.is_ai.is_(True)))
    ai_user = ai_result.scalar_one_or_none()
    if not ai_user:
        return {"error": "AI opponent not found. Run ensure_ai_user first."}

    total_needed = CARDS_PER_PLAYER * 2
    driver_count = await session.execute(select(func.count(Driver.id)))
    if driver_count.scalar() < total_needed:
        return {"error": "Not enough drivers in the database."}

    all_driver_ids = [
        row[0] for row in (await session.execute(select(Driver.id))).all()
    ]
    selected_drivers = random.sample(all_driver_ids, total_needed)
    user_driver_ids = selected_drivers[:CARDS_PER_PLAYER]
    ai_driver_ids = selected_drivers[CARDS_PER_PLAYER:]

    all_track_ids = [row[0] for row in (await session.execute(select(Track.id))).all()]
    selected_track_ids = random.sample(all_track_ids, ROUNDS_PER_GAME)

    game = Game(user_id=user_id, ai_user_id=ai_user.id)
    session.add(game)
    await session.flush()

    for did in user_driver_ids:
        session.add(GamePlayerHand(game_id=game.id, user_id=user_id, driver_id=did))
    for did in ai_driver_ids:
        session.add(GamePlayerHand(game_id=game.id, user_id=ai_user.id, driver_id=did))

    for rn, tid in enumerate(selected_track_ids, start=1):
        session.add(GameRound(game_id=game.id, round_number=rn, track_id=tid))

    await session.flush()

    user_cards = await load_hand_details(session, game.id, user_id)
    first_track = await load_track_details(session, selected_track_ids[0])

    return {
        "game_id": game.id,
        "your_cards": user_cards,
        "round": 1,
        "track": first_track,
        "message": f"Game started! You have {CARDS_PER_PLAYER} cards. Round 1 track is {first_track['name']}. Play a card!",
    }


# ── Play card ─────────────────────────────────────────────────────────────


async def play_round(
    session: AsyncSession, game_id: int, user_id: int, driver_id: int
) -> dict:
    """Execute a single round: user plays a card, AI responds.

    Validates the card, runs AI selection, computes power scores for
    both players, determines the round winner, and updates scores.
    Automatically finalizes the game after round 5.

    Args:
        session: Active database session (inside a transaction).
        game_id: ID of the current game.
        user_id: ID of the human player.
        driver_id: Driver ID the user wants to play this round.

    Returns:
        Dict with round result (cards, powers, winner, score), plus
        next-round info or game_over summary if final round.
    """
    game = await session.get(Game, game_id)
    if not game:
        return {"error": f"Game {game_id} not found."}
    if game.status != "in_progress":
        return {"error": "This game is already completed."}
    if game.user_id != user_id:
        return {"error": "This is not your game."}

    hand_entry = await session.execute(
        select(GamePlayerHand).where(
            GamePlayerHand.game_id == game_id,
            GamePlayerHand.user_id == user_id,
            GamePlayerHand.driver_id == driver_id,
            GamePlayerHand.is_played.is_(False),
        )
    )
    card = hand_entry.scalar_one_or_none()
    if not card:
        return {"error": f"Driver {driver_id} is not in your hand or already played."}

    current_round = await session.execute(
        select(GameRound).where(
            GameRound.game_id == game_id,
            GameRound.round_number == game.current_round,
        )
    )
    game_round = current_round.scalar_one()
    track_id = game_round.track_id

    card.is_played = True

    ai_driver_id = await ai_select_card(session, game_id, game.ai_user_id)
    ai_hand = await session.execute(
        select(GamePlayerHand).where(
            GamePlayerHand.game_id == game_id,
            GamePlayerHand.user_id == game.ai_user_id,
            GamePlayerHand.driver_id == ai_driver_id,
        )
    )
    ai_hand.scalar_one().is_played = True

    user_base = await compute_base_power(session, driver_id)
    ai_base = await compute_base_power(session, ai_driver_id)
    user_mult = await get_track_multiplier(session, driver_id, track_id)
    ai_mult = await get_track_multiplier(session, ai_driver_id, track_id)
    user_power = round(user_base * user_mult, 2)
    ai_power = round(ai_base * ai_mult, 2)

    if user_power > ai_power:
        winner = "user"
        game.user_score += POINTS_PER_ROUND_WIN
    elif ai_power > user_power:
        winner = "ai"
        game.ai_score += POINTS_PER_ROUND_WIN
    else:
        winner = "draw"
        game.user_score += POINTS_PER_ROUND_DRAW
        game.ai_score += POINTS_PER_ROUND_DRAW

    game_round.user_driver_id = driver_id
    game_round.ai_driver_id = ai_driver_id
    game_round.user_power = user_power
    game_round.ai_power = ai_power
    game_round.winner = winner

    user_driver = await session.get(Driver, driver_id)
    ai_driver = await session.get(Driver, ai_driver_id)
    track = await session.get(Track, track_id)

    result = {
        "round": game.current_round,
        "track": track.name,
        "your_card": f"{user_driver.name} (#{user_driver.number})",
        "your_base_power": user_base,
        "your_track_multiplier": user_mult,
        "your_power": user_power,
        "ai_card": f"{ai_driver.name} (#{ai_driver.number})",
        "ai_base_power": ai_base,
        "ai_track_multiplier": ai_mult,
        "ai_power": ai_power,
        "round_winner": winner,
        "score": f"You {game.user_score} - {game.ai_score} AI",
    }

    is_final = game.current_round >= ROUNDS_PER_GAME
    if is_final:
        result["game_over"] = await _finalize_game(session, game)
    else:
        game.current_round += 1
        next_round = await session.execute(
            select(GameRound).where(
                GameRound.game_id == game_id,
                GameRound.round_number == game.current_round,
            )
        )
        next_track_details = await load_track_details(
            session, next_round.scalar_one().track_id
        )
        remaining = await load_hand_details(session, game_id, user_id)
        result["next_round"] = game.current_round
        result["next_track"] = next_track_details
        result["remaining_cards"] = remaining

    await session.flush()
    return result


# ── End game ──────────────────────────────────────────────────────────────


async def _finalize_game(session: AsyncSession, game: Game) -> dict:
    """Determine the overall winner and update lifetime stats.

    Scoring formula:
      winner  → (2 × rounds_won) + 5
      loser   → (2 × rounds_won) - 5
      draw    → (2 × rounds_won) for each player (no bonus/penalty)

    Args:
        session: Active database session.
        game: The Game ORM object to finalize.

    Returns:
        Dict with result string, final score, points earned for
        both players, and the user's updated total points.
    """
    game.status = "completed"
    game.completed_at = datetime.now(timezone.utc)

    user = await session.get(User, game.user_id)
    ai = await session.get(User, game.ai_user_id)

    user.games_played += 1
    ai.games_played += 1

    user_rounds_won = game.user_score // POINTS_PER_ROUND_WIN
    ai_rounds_won = game.ai_score // POINTS_PER_ROUND_WIN

    if game.user_score > game.ai_score:
        overall = "You win!"
        user_pts = (2 * user_rounds_won) + POINTS_GAME_WIN_BONUS
        ai_pts = (2 * ai_rounds_won) - POINTS_GAME_LOSS_PENALTY
        user.wins += 1
        ai.losses += 1
    elif game.ai_score > game.user_score:
        overall = "AI wins!"
        user_pts = (2 * user_rounds_won) - POINTS_GAME_LOSS_PENALTY
        ai_pts = (2 * ai_rounds_won) + POINTS_GAME_WIN_BONUS
        user.losses += 1
        ai.wins += 1
    else:
        overall = "It's a draw!"
        user_pts = 2 * user_rounds_won
        ai_pts = 2 * ai_rounds_won

    user.total_points += user_pts
    ai.total_points += ai_pts

    return {
        "result": overall,
        "final_score": f"You {game.user_score} - {game.ai_score} AI",
        "your_rounds_won": user_rounds_won,
        "ai_rounds_won": ai_rounds_won,
        "your_points_earned": user_pts,
        "ai_points_earned": ai_pts,
        "your_total_points": user.total_points,
    }
