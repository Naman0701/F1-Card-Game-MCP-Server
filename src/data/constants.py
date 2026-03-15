"""
Application-level constants and configuration values.
"""

import re

# ---------------------------------------------------------------------------
# App-level constants
# ---------------------------------------------------------------------------
NAME_PATTERN = re.compile(r"^[A-Za-z0-9_]{2,20}$")
NAME_MIN_LENGTH = 2
NAME_MAX_LENGTH = 20

ERGAST_BASE_URL = "https://api.jolpi.ca/ergast/f1"

DEFAULT_DB_URL = "postgresql+asyncpg://localhost:5432/f1mcp"

POINTS_PER_ROUND_WIN = 2
POINTS_PER_ROUND_DRAW = 1
POINTS_GAME_WIN_BONUS = 5
POINTS_GAME_LOSS_PENALTY = 5

CARDS_PER_PLAYER = 5
ROUNDS_PER_GAME = 5

TRACK_MULTIPLIER_MIN = 0.5
TRACK_MULTIPLIER_MAX = 2.0
TRACK_MULTIPLIER_DEFAULT = 1.0

SKILL_VALUE_MIN = 0
SKILL_VALUE_MAX = 100
