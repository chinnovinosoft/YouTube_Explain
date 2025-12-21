import asyncpg
import logging
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)

# MCP Server
mcp = FastMCP("customer-postgres-mcp")

# Postgres Config
DB_CONFIG = {
    "user": "postgres",
    "password": "postgres",
    "database": "mcp_langgraph",
    "host": "localhost",
    "port": 5432
}

# MCP Tool
@mcp.tool()
async def get_customer_info(id: int) -> str:
    """
    Get customer details using id.

    Args:
        id: Unique customer identifier

    Returns:
        Customer details or not-found message
    """
    query = """
        SELECT id, name, city, dob, designation
        FROM customers
        WHERE id = $1
    """

    async with asyncpg.create_pool(**DB_CONFIG) as pool:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, id)

    if not row:
        return f"No customer found with id = {id}"

    return (
        f"Customer Details:\n"
        f"- ID: {row['id']}\n"
        f"- Name: {row['name']}\n"
        f"- City: {row['city']}\n"
        f"- DOB: {row['dob']}\n"
        f"- Designation: {row['designation']}"
    )

# ----------------------------------
# Run MCP Server (STDIO)
# ----------------------------------
def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
