# F1 Card Game - MCP Server

A Formula 1 themed card game built as an MCP (Model Context Protocol) server. Players compete against an AI opponent using real F1 driver cards, where each driver's skills and track affinity determine the outcome.

---

## Game Overview

Two players (human + AI) each receive 5 random F1 driver cards. Over 5 rounds, tracks are revealed one-by-one, and both players simultaneously play a card. The driver's skills combined with their track multiplier determine the round winner. After all 5 rounds, the overall winner earns leaderboard points.

---

## Database Schema

### Core Tables

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Country    │     │    Team      │     │    Track     │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ id (PK)      │◄──┐ │ id (PK)      │     │ id (PK)      │
│ name         │   │ │ name         │     │ name         │
│ code         │   │ │ country_id(FK)│────►│ country_id(FK)│───┐
└──────────────┘   │ │ logo_url     │     │ laps         │   │
                   │ └──────────────┘     │ circuit_type │   │
                   │        │             └──────────────┘   │
                   │        │                                │
                   └────────┼────────────────────────────────┘
                            │
                   ┌────────┴───────┐
                   │ TeamDriverRel  │
                   ├────────────────┤
                   │ id (PK)        │
                   │ team_id (FK)   │
                   │ driver_id (FK) │
                   │ season_year    │
                   └────────┬───────┘
                            │
                   ┌────────┴───────┐     ┌──────────────┐
                   │    Driver      │     │    Skill     │
                   ├────────────────┤     ├──────────────┤
                   │ id (PK)        │     │ id (PK)      │
                   │ name           │     │ name         │
                   │ number         │     │ description  │
                   │ country_id(FK) │     └──────┬───────┘
                   │ avatar_url     │            │
                   └───┬────────┬───┘            │
                       │        │       ┌────────┴────────┐
                       │        │       │DriverSkillRel   │
                       │        │       ├─────────────────┤
                       │        └──────►│ driver_id (FK)  │
                       │                │ skill_id (FK)   │
                       │                │ value (0-100)   │
                       │                └─────────────────┘
                       │
              ┌────────┴──────────┐
              │ DriverTrackRel    │
              ├───────────────────┤
              │ driver_id (FK)    │
              │ track_id (FK)     │
              │ multiplier (0.5-2)│
              └───────────────────┘
```

### Game Tables

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐
│    User      │     │      Game        │     │   GameRound      │
├──────────────┤     ├──────────────────┤     ├──────────────────┤
│ id (PK)      │◄──┐ │ id (PK)          │◄────│ id (PK)          │
│ name         │   │ │ user_id (FK)     │     │ game_id (FK)     │
│ total_points │   │ │ ai_user_id (FK)  │     │ round_number(1-5)│
│ games_played │   └─│ status           │     │ track_id (FK)    │
│ wins         │     │ user_score       │     │ user_driver_id   │
│ losses       │     │ ai_score         │     │ ai_driver_id     │
│ is_ai        │     │ created_at       │     │ user_power       │
│ created_at   │     │ completed_at     │     │ ai_power         │
└──────────────┘     └──────────────────┘     │ winner (user/ai) │
                                              └──────────────────┘

┌───────────────────┐
│   GamePlayerHand  │
├───────────────────┤
│ id (PK)           │
│ game_id (FK)      │
│ user_id (FK)      │
│ driver_id (FK)    │
│ is_played         │
└───────────────────┘
```

### The 6 Skills

| Skill           | Description                           |
|-----------------|---------------------------------------|
| `pace`          | Raw single-lap speed                  |
| `racecraft`     | Wheel-to-wheel racing ability         |
| `awareness`     | Spatial awareness and avoiding incidents |
| `experience`    | Career experience and consistency     |
| `wet_weather`   | Performance in rain conditions        |
| `tire_management` | Ability to preserve tires over stints |

---

## Game Flow

### High-Level Flow

```
User: "I want to play"
        │
        ▼
┌─────────────────┐    new user?    ┌─────────────────┐
│  start_game()   │───────yes──────►│    welcome()    │
│                 │                 │ (name + password)│
│                 │◄────────────────└─────────────────┘
│                 │
│  - Pick 5 random drivers for user
│  - Pick 5 random drivers for AI   (no overlap)
│  - Pick 5 random tracks
│  - Create Game record (status="in_progress")
│  - Create GamePlayerHand records
│  - Return user's hand (cards) + round 1 info
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│              ROUND LOOP (×5)                │
│                                             │
│  1. Reveal track for this round             │
│  2. Show user their remaining cards         │
│  3. User picks a driver card: play_card()   │
│  4. AI picks a random card                  │
│  5. Compute power scores for both           │
│  6. Determine round winner (+2 points)      │
│  7. Mark both cards as played               │
│  8. Return round result                     │
│                                             │
│  Repeat until round 5 complete              │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│              GAME END                       │
│                                             │
│  - Compare final scores                     │
│  - Winner: +5 total points                  │
│  - Loser:  -5 total points                  │
│  - Draw:   +0 total points (no change)      │
│  - Update User.total_points, games_played,  │
│    wins/losses                              │
│  - Set Game.status = "completed"            │
│  - Return final summary                     │
└─────────────────────────────────────────────┘
```

### Detailed Round Resolution

```
         User plays Driver X on Track T
         AI   plays Driver Y on Track T
                    │
                    ▼
    ┌───────────────────────────────┐
    │     Compute Power Score       │
    │                               │
    │  avg_skill = mean of all 6    │
    │    skill values for driver    │
    │                               │
    │  multiplier = DriverTrackRel  │
    │    .multiplier for this       │
    │    driver + track combo       │
    │    (default 1.0 if no entry)  │
    │                               │
    │  power = avg_skill * multiplier│
    └───────────────┬───────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │  Compare: user_power vs       │
    │           ai_power            │
    │                               │
    │  Higher power wins the round  │
    │  Winner gets +2 to game score │
    │                               │
    │  Exact tie: both get +1       │
    └───────────────────────────────┘
```

---

## Identified Gaps & Design Decisions

### Gap 1: Tie-Breaking (Game Level)
**Problem**: What happens when both players end with the same score after 5 rounds (e.g., 4-4 with a tied round)?
**Decision**: A draw awards +0 total points to both players. No wins/losses are recorded; only `games_played` is incremented.

### Gap 2: Which Skill Is Used?
**Problem**: Each driver has 6 skills, but how do they translate into a single "power" value per round?
**Decision**: Use the **average of all 6 skills** multiplied by the track multiplier. This keeps it simple and ensures all skills matter. Future enhancement: certain tracks could weight specific skills (e.g., Monaco weights `awareness` higher).

### Gap 3: Round Tie-Breaking
**Problem**: What if both drivers have identical power scores in a round?
**Decision**: Both players receive +1 point each (split).

### Gap 4: AI Card Selection Strategy
**Problem**: How does the AI choose which card to play?
**Decision**: AI picks a **random** unplayed card from its hand. This keeps the game fair and unpredictable — the AI has no knowledge of the current track. Can be improved later with difficulty levels that use track-aware selection.

### Gap 5: Driver Assignment Overlap
**Problem**: Can both players receive the same driver?
**Decision**: **No**. The 10 drivers are drawn from the pool without replacement. Each driver appears in at most one hand per game.

### Gap 6: Card Play Order / Simultaneity
**Problem**: In MCP, the user must act first via a tool call. The AI "responds" after. This means the user commits before seeing the AI's choice.
**Decision**: This is fine — it mirrors real card games. The user picks first (blind to AI's choice), then the AI picks, then both are revealed. Neither player sees the other's hand.

### Gap 7: AI as a Persistent User
**Problem**: "AI will always be a player" — is there one AI user or one per game?
**Decision**: A **single persistent AI user** record (`is_ai=true`) exists in the `users` table. All games reference this same AI user. Its `total_points`, `wins`, `losses` are tracked like any other player.

### Gap 8: Track Multiplier Defaults
**Problem**: Not every driver will have an entry in `DriverTrackRel` for every track.
**Decision**: If no `DriverTrackRel` entry exists for a driver+track pair, default to a multiplier of **1.0** (neutral).

### Gap 9: Data Seeding
**Problem**: Where does the initial data (drivers, teams, tracks, skills) come from?
**Decision**: Use the **FastF1** library to pull real F1 data for the current season. Skill values will be derived from actual performance metrics (qualifying pace, race pace, consistency, etc.) and normalized to 0-100. Track multipliers can be computed from historical driver performance at each circuit.

### Gap 10: Game State Persistence
**Problem**: MCP is stateless between tool calls. How do we track which round we're on, which cards are played, etc.?
**Decision**: All game state is stored in the **database**. Each tool call reads the current game state (via `Game`, `GameRound`, `GamePlayerHand` tables) and advances it. The `game_id` is the key to resume any game.

### Gap 11: Viewing Game Info
**Problem**: How does the user see their cards, scores, or the leaderboard?
**Decision**: Dedicated read-only tools (`get_hand`, `get_game_status`, `get_leaderboard`) provide this information at any time during or after a game.

### Gap 12: Multiple Concurrent Games
**Problem**: Can a user have multiple active games?
**Decision**: **No**. A user can only have one `in_progress` game at a time. They must complete or abandon the current game before starting a new one.

---

## MCP Tools (Server API)

### User Tools

| Tool | Description | Parameters | Returns |
|------|-------------|------------|---------|
| `welcome` | Register or log in | `name: str, password: str` | Welcome message with user_id and stats |
| `update_password` | Change account password | `user_id: int, new_password: str, current_password: str` | Confirmation message |
| `logout` | End the current session | `user_id: int` | Goodbye message |
| `ensure_ai_user` | Create the AI opponent if missing | — | AI user confirmation |

### Game Tools

| Tool | Description | Parameters | Returns |
|------|-------------|------------|---------|
| `start_game` | Start a new game, deal cards, pick tracks | `user_id: int` | Game id, user's 5 driver cards (with skills), round 1 track |
| `play_card` | Play a driver card for the current round | `game_id: int, driver_id: int` | Round result: both cards revealed, power scores, winner, updated game score |

### Query Tools

| Tool | Description | Parameters | Returns |
|------|-------------|------------|---------|
| `get_hand` | View remaining cards in your hand | `game_id: int` | List of unplayed driver cards with skills |
| `get_game_status` | View current game state | `game_id: int` | Current round, scores, past round results, upcoming track |
| `get_leaderboard` | View top players by total points | `top_n: int (default 10), include_ai: bool` | Ranked list of players with stats |

### MCP Resources (read-only)

| URI | Description |
|-----|-------------|
| `f1cardgame://rules` | Complete rules and scoring guide |
| `f1cardgame://skills` | Definitions of the 6 driver skills |
| `f1cardgame://drivers` | Full driver catalog with skills and teams |
| `f1cardgame://tracks` | Full track catalog with circuit types |

---

## Project Structure

```
f1-mcp-server/
├── server.py                  # MCP server entry point, tool/resource registration
├── alembic.ini                # Alembic configuration
├── pyproject.toml             # Dependencies and project config
│
├── src/
│   ├── data/
│   │   └── constants.py       # F1 reference data: drivers, teams, tracks, skills
│   │
│   ├── models/                # SQLAlchemy async ORM models
│   │   ├── base.py            # Base model, async engine, session factory
│   │   ├── country.py
│   │   ├── team.py
│   │   ├── driver.py
│   │   ├── track.py
│   │   ├── skill.py
│   │   ├── user.py
│   │   ├── game.py            # Game, GameRound, GamePlayerHand
│   │   └── relations.py       # TeamDriverRel, DriverSkillRel, DriverTrackRel
│   │
│   ├── services/              # Business logic
│   │   ├── fetch_service.py   # FastF1/Ergast data enrichment + skill computation
│   │   ├── seed_service.py    # Database seeding orchestrator
│   │   ├── power_service.py   # Base power and track-adjusted power calculation
│   │   ├── game_service.py    # Game creation, round resolution, scoring
│   │   └── query_service.py   # Hand inspection, game status, leaderboard
│   │
│   ├── tools/                 # MCP tool implementations
│   │   ├── user_tools.py      # welcome, update_password, logout, ensure_ai_user
│   │   ├── game_tools.py      # start_game, play_card
│   │   └── query_tools.py     # get_hand, get_game_status, get_leaderboard
│   │
│   └── resources/
│       └── game_resources.py  # MCP resources: rules, skills, drivers, tracks
│
├── alembic/                   # Database migrations
│   ├── env.py
│   └── versions/
│
└── tests/
    ├── conftest.py            # Shared fixtures (in-memory SQLite)
    ├── unit/                  # Unit tests for each module
    └── functional/            # End-to-end auth and game flow tests
```

---

## Power Score Formula

```
power = average(pace, racecraft, awareness, experience, wet_weather, tire_management) × track_multiplier
```

**Example:**
- Driver: Max Verstappen — skills: [95, 92, 88, 80, 90, 85] → avg = 88.33
- Track: Spa-Francorchamps — multiplier for Verstappen: 1.6
- **Power = 88.33 × 1.6 = 141.33**

vs.

- Driver: Lando Norris — skills: [88, 85, 82, 65, 78, 80] → avg = 79.67
- Track: Spa-Francorchamps — multiplier for Norris: 1.2
- **Power = 79.67 × 1.2 = 95.60**

**Verstappen wins this round. +2 to that player's game score.**

---

## Tech Stack

- **Python 3.13+**
- **FastMCP** — MCP server framework
- **SQLAlchemy 2.0** (async) — ORM
- **asyncpg** — PostgreSQL async driver
- **Alembic** — Database migrations
- **FastF1** — Real F1 data sourcing
- **PostgreSQL** — Database

---

## Getting Started

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- PostgreSQL running locally or remotely

### Setup

```bash
# Clone and install dependencies
git clone <repo-url>
cd f1-mcp-server
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL and AUTH_SECRET_KEY

# Run database migrations
uv run alembic upgrade head

# Seed F1 data (drivers, teams, tracks, skills, multipliers)
uv run python -m src.services.seed_service

# Run the MCP server
uv run python server.py
```

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL async connection string | `postgresql+asyncpg://user:pass@localhost:5432/f1mcp` |
| `AUTH_SECRET_KEY` | Secret key for password hashing | Any random string |
