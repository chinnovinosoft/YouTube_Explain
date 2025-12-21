from mcp.server.fastmcp import FastMCP, Context
from pydantic import BaseModel
import asyncpg
from datetime import date

mcp = FastMCP("customer-elicitation-server")

DB_CONFIG = {
    "user": "postgres",
    "password": "postgres",
    "database": "mcp_langgraph",
    "host": "localhost",
    "port": 5432,
}

class Confirmation(BaseModel):
    confirm: bool

@mcp.tool()
async def create_customer(
    id: int,
    name: str,
    city: str,
    dob: str,
    designation: str,
    ctx: Context,
) -> str:
    result = await ctx.elicit(
        message=(
            f"Please confirm customer details:\n"
            f"ID: {id}\n"
            f"Name: {name}\n"
            f"City: {city}\n"
            f"DOB: {dob}\n"
            f"Designation: {designation}\n\n"
            f"Confirm?"
        ),
        schema=Confirmation,
    )

    if result.action == "cancel":
        return "Operation cancelled by user."

    if result.action == "decline":
        return "User declined to confirm. Customer not created."

    if result.action == "accept" and result.data and result.data.confirm:
        dob_date = date.fromisoformat(dob)

        conn = await asyncpg.connect(**DB_CONFIG)

        await conn.execute(
            """
            INSERT INTO customers (id, name, city, dob, designation)
            VALUES ($1, $2, $3, $4, $5)
            """,
            id,
            name,
            city,
            dob_date,
            designation,
        )

        await conn.close()

        return f"Customer {name} successfully created."

    return "Confirmation not received. No action taken."

if __name__ == "__main__":
    mcp.run(transport="stdio")
