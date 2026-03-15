import random
from fastmcp import FastMCP

mcp = FastMCP(name="Demo MCP Server")


@mcp.tool()
def roll_dice():
    """Roll a 6-sided dice"""
    return random.randint(1, 6)


@mcp.tool()
def get_percentage(num: int, total: int) -> str:
    """Get the percentage of a number"""
    return f"{round((num / total) * 100, 2)}%"


if __name__ == "__main__":
    mcp.run(transport='http', host='0.0.0.0', port=8000)
