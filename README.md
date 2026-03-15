# 🏎️ F1 MCP Server

An F1 data intelligence MCP (Model Context Protocol) server powered by **FastF1** and **PostgreSQL**.

Query, analyze, and compare Formula 1 data — from race results and lap times to telemetry and tire strategies — all through AI assistants.

## Features

- **Race Results & Standings** — Query race results, driver standings, and constructor standings
- **Lap Time Analysis** — Compare lap times between drivers across sessions
- **Tire Strategy Analyzer** — Analyze tire compounds, stint lengths, and pit stop timings
- **Telemetry Deep Dive** — Access speed, throttle, brake, gear, and DRS data per lap
- **Head-to-Head Comparisons** — Compare teammates and rivals across qualifying and race
- **Weather Impact Analysis** — Correlate weather conditions with performance
- **Data Sync** — Sync F1 data from FastF1 into PostgreSQL on-demand

## Tech Stack

| Component | Technology |
|-----------|------------|
| MCP Framework | `fastmcp` |
| F1 Data | `fastf1` |
| Database | PostgreSQL + `sqlalchemy` |
| Migrations | `alembic` |
| HTTP Client | `httpx` |

## Why FastMCP over the Official MCP SDK?

This project uses **FastMCP** instead of the official MCP Python SDK (`mcp`). Here's why:

| Aspect | MCP SDK (Official) | FastMCP ✅ |
|--------|-------------------|----------------------|
| **Abstraction** | Lower-level, closer to the raw MCP spec | Higher-level, Pythonic framework |
| **Boilerplate** | Manual schema, validation, and wiring | Decorators auto-generate schemas and docs |
| **Speed** | More setup work | Ship tools fast with minimal code |
| **Extras** | Core primitives only | OpenAPI integration, OAuth, proxy servers, background tasks |
| **Backed by** | Anthropic | PrefectHQ |
| **Install** | `pip install "mcp[cli]"` | `pip install fastmcp` |

**Why FastMCP fits this project:** With many tools to build (results, laps, telemetry, strategy, etc.), FastMCP's decorator-driven approach keeps each tool definition clean and focused on the business logic — no protocol plumbing needed.

> **Note:** FastMCP is built on top of the official MCP SDK, so it's fully spec-compliant. You can always drop down to the lower-level SDK if needed.

## FastMCP 3.0 vs 2.0 — CLI Command Reference

FastMCP 3.0 introduced significant CLI changes. Here's a full comparison:

### Command Comparison

| Task | FastMCP 2.0 | FastMCP 3.0 | Notes |
|------|-------------|-------------|-------|
| **Run a server** | `fastmcp run server.py` | `fastmcp run server.py` | Same syntax, but 3.0 adds config file auto-detection |
| **Run over HTTP** | `fastmcp run server.py -t http` | `fastmcp run server.py -t http` | Unchanged |
| **Dev with Inspector** | `fastmcp dev server.py` | `fastmcp dev inspector server.py` | 3.0 adds `inspector` subcommand |
| **Install to Claude Desktop** | `fastmcp install claude-desktop server.py` | `fastmcp install claude-desktop server.py` | 3.0 adds Gemini CLI & Goose support |
| **Install to Cursor** | `fastmcp install cursor server.py` | `fastmcp install cursor server.py` | Unchanged |
| **Generate MCP JSON** | `fastmcp install mcp-json server.py` | `fastmcp install mcp-json server.py` | Unchanged |
| **Inspect server** | `fastmcp inspect server.py` | `fastmcp inspect server.py` | 3.0 adds `--format mcp` for protocol-level view |
| **List tools** | — | `fastmcp list server.py` | New in 3.0 |
| **Call a tool** | — | `fastmcp call server.py tool_name arg=val` | New in 3.0 |
| **Discover configured servers** | — | `fastmcp discover` | New in 3.0 — scans Claude, Cursor, Gemini, Goose |
| **Generate CLI from server** | — | `fastmcp generate-cli server.py` | New in 3.0 — scaffolds a typed CLI |
| **OAuth CIMD management** | — | `fastmcp auth cimd` | New in 3.0 |
| **Pre-build environment** | `fastmcp project prepare` | `fastmcp project prepare` | Unchanged |
| **Show version** | `fastmcp version` | `fastmcp version` | 3.0 adds `--copy` flag |

### Key Breaking Changes in 3.0

| Change | 2.0 | 3.0 |
|--------|-----|-----|
| Dev command | `fastmcp dev server.py` | `fastmcp dev inspector server.py` |
| Dev auto-reload | Not default | On by default (`--no-reload` to disable) |
| Server target resolution | File-based only | Files, URLs, config files, and **name-based** resolution (`fastmcp list weather`) |
| HTTP auth | Not supported | OAuth built-in; `--auth none` to skip, `--auth "Bearer ..."` for tokens |
| Transport override | N/A | `--transport sse` to force SSE for older servers |
| Inspect output | Text summary + FastMCP JSON | Text summary + `--format fastmcp` or `--format mcp` |

### New in 3.0 — Name-Based Server Resolution

In 3.0, you can refer to servers by name if they're configured in an editor:

```bash
fastmcp list weather
fastmcp call weather get_forecast city=London
fastmcp call cursor:weather get_forecast city=London   # scope to a specific editor
fastmcp discover                                        # see all configured servers
```

## Project Structure

```
f1-mcp/
├── pyproject.toml
├── README.md
├── .env.example
├── src/
│   ├── __init__.py
│   ├── server.py              # MCP server entry point
│   ├── config.py              # Configuration & env loading
│   ├── db/
│   │   ├── __init__.py
│   │   ├── connection.py      # Database connection setup
│   │   ├── models.py          # SQLAlchemy models
│   │   └── queries.py         # Reusable SQL queries
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── results.py         # Race results & standings tools
│   │   ├── laps.py            # Lap time analysis tools
│   │   ├── telemetry.py       # Telemetry data tools
│   │   ├── strategy.py        # Tire & pit strategy tools
│   │   ├── comparison.py      # Head-to-head comparison tools
│   │   └── sync.py            # FastF1 → Postgres data sync
│   └── resources/
│       ├── __init__.py
│       └── standings.py       # MCP resources
├── migrations/
│   ├── env.py
│   └── versions/
└── tests/
    ├── __init__.py
    ├── test_results.py
    ├── test_laps.py
    └── test_strategy.py
```

## Setup

### 1. Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- PostgreSQL running locally or remotely

### 2. Install Dependencies

```bash
uv sync
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials
```

### 4. Run Database Migrations

```bash
alembic upgrade head
```

### 5. Run the MCP Server

```bash
uv run fastmcp run src/server.py
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://localhost:5432/f1mcp` |
| `FASTF1_CACHE_DIR` | Cache directory for FastF1 data | `./.f1cache` |

## License

MIT
