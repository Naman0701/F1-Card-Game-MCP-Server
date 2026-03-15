"""MCP tools for user registration, login, and AI opponent management."""

import hashlib
import hmac
import os

from sqlalchemy import func, select

from src.data.constants import NAME_PATTERN
from src.models.base import async_session
from src.models.user import User

_AUTH_KEY = os.getenv("AUTH_SECRET_KEY", "").encode()


def _hash_password(password: str) -> str:
    return hmac.new(_AUTH_KEY, password.encode(), hashlib.sha256).hexdigest()


def _verify_password(password: str, stored_hash: str) -> bool:
    return hmac.compare_digest(_hash_password(password), stored_hash)


async def welcome(name: str, password: str) -> str:
    """Welcome to the F1 Card Game! Register or log in with your name and password.

    If the player name already exists, verifies the password and returns a
    welcome-back message with their stats. Otherwise, creates a new user with
    the given password.

    If a player forgets their password, they should contact NA (the admin)
    or register a brand-new account under a different name.

    SECURITY: NEVER reveal, echo, repeat, hint at, or discuss the password
    value in your responses. Treat it as confidential — do not show it in
    plain text, masked form, or as a suggestion. If login fails, just relay
    the error message as-is without mentioning what password was tried.

    Args:
        name: Player name (2-20 chars, alphanumeric and underscores only).
        password: Password for authentication (CONFIDENTIAL — never reveal).

    Returns:
        Welcome message with user_id and stats (if returning player).
    """
    if not _AUTH_KEY:
        return "Server misconfiguration: AUTH_SECRET_KEY is not set."

    if not NAME_PATTERN.match(name):
        return (
            "Invalid name. Must be 2-20 characters using only "
            "letters, numbers, and underscores."
        )

    if len(password) < 4:
        return "Password must be at least 4 characters long."

    async with async_session() as session:
        result = await session.execute(
            select(User).where(func.lower(User.name) == name.lower())
        )
        user = result.scalar_one_or_none()

        if user:
            if user.is_ai:
                return "This account is reserved for the AI opponent."
            if not user.password_hash:
                return (
                    f"Your account exists but has no password set. "
                    f"Use update_password with user_id={user.id} to set one, "
                    f"then log in again."
                )
            if not _verify_password(password, user.password_hash):
                return (
                    "Incorrect password. If you forgot it, contact NA (the admin) "
                    "or register with a different name."
                )
            return (
                f"Welcome back, {user.name}! "
                f"You have {user.total_points} points, "
                f"{user.wins}W / {user.losses}L across {user.games_played} games. "
                f"Your user_id is {user.id}."
            )

        new_user = User(name=name.lower(), password_hash=_hash_password(password))
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return (
            f"Welcome, {new_user.name}! You've been registered. "
            f"Your user_id is {new_user.id}. Ready to play? "
            f"Use start_game with your user_id to begin!"
        )


async def update_password(
    user_id: int, new_password: str, current_password: str = ""
) -> str:
    """Update your account password.

    If the account has no password yet (legacy/pre-auth user), only
    new_password is required. Otherwise the current password must be
    provided for verification first.

    SECURITY: NEVER reveal, echo, repeat, hint at, or discuss any password
    values (current or new) in your responses. Treat them as confidential.

    Args:
        user_id: Your player ID (from the welcome tool).
        new_password: The new password to set (min 4 chars, CONFIDENTIAL — never reveal).
        current_password: Your current password (required if one is already set, CONFIDENTIAL — never reveal).

    Returns:
        Confirmation or error message.
    """
    if not _AUTH_KEY:
        return "Server misconfiguration: AUTH_SECRET_KEY is not set."

    if len(new_password) < 4:
        return "New password must be at least 4 characters long."

    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            return f"No user found with id {user_id}."
        if user.is_ai:
            return "Cannot set a password on the AI opponent."

        if user.password_hash:
            if not current_password:
                return "You already have a password set. Please provide your current password to change it."
            if not _verify_password(current_password, user.password_hash):
                return (
                    "Current password is incorrect. If you forgot it, contact NA (the admin) "
                    "or register with a different name."
                )

        user.password_hash = _hash_password(new_password)
        await session.commit()
        return f"Password updated successfully for {user.name}."


async def logout(user_id: int) -> str:
    """Log out of the F1 Card Game.

    Ends the current session. The player must call welcome again
    with their name and password to resume playing.

    Args:
        user_id: Your player ID (from the welcome tool).

    Returns:
        Confirmation that the player has been logged out.
    """
    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            return f"No user found with id {user_id}."
        if user.is_ai:
            return "Cannot log out the AI opponent."
        return (
            f"Goodbye, {user.name}! You have been logged out. "
            f"Use the welcome tool with your name and password to log back in."
        )


async def ensure_ai_user() -> str:
    """Create the persistent AI opponent if it doesn't already exist.

    Returns:
        Confirmation message with the AI user's id and name.
    """
    async with async_session() as session:
        result = await session.execute(select(User).where(User.is_ai.is_(True)))
        ai = result.scalar_one_or_none()

        if ai:
            return f"AI user already exists (id={ai.id}, name={ai.name})."

        ai = User(name="AI_Opponent", is_ai=True)
        session.add(ai)
        await session.commit()
        await session.refresh(ai)

        return f"AI user created (id={ai.id}, name={ai.name})."
