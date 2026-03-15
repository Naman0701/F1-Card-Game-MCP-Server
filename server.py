from dotenv import load_dotenv

load_dotenv()

from fastmcp import FastMCP  # noqa: E402

from src.resources.game_resources import (
    get_drivers,
    get_rules,
    get_skills,
    get_tracks,
)  # noqa: E402
from src.tools.game_tools import play_card, start_game  # noqa: E402
from src.tools.query_tools import (
    get_game_status,
    get_hand,
    get_leaderboard,
)  # noqa: E402
from src.tools.user_tools import (
    ensure_ai_user,
    logout,
    update_password,
    welcome,
)  # noqa: E402

mcp = FastMCP(name="F1 Card Game", version="1.0.0")

mcp.resource("f1cardgame://rules")(get_rules)
mcp.resource("f1cardgame://skills")(get_skills)
mcp.resource("f1cardgame://drivers")(get_drivers)
mcp.resource("f1cardgame://tracks")(get_tracks)

mcp.tool()(welcome)
mcp.tool()(update_password)
mcp.tool()(logout)
mcp.tool()(ensure_ai_user)
mcp.tool()(start_game)
mcp.tool()(play_card)
mcp.tool()(get_hand)
mcp.tool()(get_game_status)
mcp.tool()(get_leaderboard)

if __name__ == "__main__":
    mcp.run(transport='http', host='0.0.0.0', port=8000)
