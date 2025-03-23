from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import pandas as pd
from sqlalchemy import create_engine,text

engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/phidata_db")
try:
    with engine.connect() as connection:
        print("Connected to PostgreSQL!")
except Exception as e:
    print("Error:", e)

mcp = FastMCP("family")

@mcp.tool()
async def get_family_details() -> str:
    """Retrieve family member details.

    Returns:
        A string representation of the family member's details from the database.
    """
    query = f"SELECT * FROM family"
    df = pd.read_sql(text(query), con=engine)
    return df.to_string(index=False)


if __name__ == "__main__":
    # Tells MCP to use stdio (standard input/output) for communication.
    # Useful for CLI-based programs that exchange messages without needing a network.
    # Other transport options (WebSockets, TCP, HTTP, gRPC) 
    mcp.run(transport='stdio')
