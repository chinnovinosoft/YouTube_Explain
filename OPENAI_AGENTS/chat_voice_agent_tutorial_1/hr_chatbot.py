import asyncio
import sqlite3
from agents import Agent, Runner, InputGuardrail, GuardrailFunctionOutput, function_tool
from pydantic import BaseModel
from typing import Optional
import dateparser
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
# -------------------- DB SETUP --------------------
conn = sqlite3.connect("interviews.db")
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS interviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate TEXT NOT NULL,
        date TEXT NOT NULL
    )
""")
conn.commit()

# -------------------- TOOLS --------------------
@function_tool
def check_availability(date: str) -> str:
    """Check if the interview slot is available on a given date."""
    conn = sqlite3.connect("interviews.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM interviews WHERE date = ?", (date,))
    count = c.fetchone()[0]
    if count >= 3:
        return f"No availability on {date}. Please choose another date."
    return f"{date} is available for interview scheduling."

@function_tool
def book_interview(candidate: str, date: str) -> str:
    """Book an interview for a candidate on a specific date."""
    conn = sqlite3.connect("interviews.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM interviews WHERE date = ?", (date,))
    count = c.fetchone()[0]
    if count >= 3:
        return f"Cannot book. {date} is already fully booked."
    c.execute("INSERT INTO interviews (candidate, date) VALUES (?, ?)", (candidate, date))
    conn.commit()
    return f"Interview booked for {candidate} on {date}."

# -------------------- GUARDRAIL --------------------
class HROutput(BaseModel):
    is_hr_related: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail Agent",
    instructions="Determine if the query is related to HR/interview scheduling.",
    output_type=HROutput,
    model="gpt-4o-mini"
)

async def hr_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    output = result.final_output_as(HROutput)
    return GuardrailFunctionOutput(
        output_info=output,
        tripwire_triggered=not output.is_hr_related
    )

# -------------------- SUB AGENTS --------------------
availability_agent = Agent(
    name="Availability Agent",
    handoff_description="Agent that checks interview availability.",
    instructions="Use the tool to check if a date is available for interviews.",
    tools=[check_availability],
    model="gpt-4o-mini"
)

booking_agent = Agent(
    name="Booking Agent",
    handoff_description="Agent that books interviews.",
    instructions="Use the tool to book an interview for a candidate on a specific date.",
    tools=[book_interview],
    model="gpt-4o-mini"
)

# -------------------- MAIN AGENT --------------------
triage_agent = Agent(
    name="HR Assistant",
    instructions="Respond politely to HR-related queries and route to appropriate agent.",
    handoffs=[availability_agent, booking_agent],
    input_guardrails=[InputGuardrail(guardrail_function=hr_guardrail)],
    model="gpt-4o-mini"
)

# -------------------- DRIVER --------------------
async def main():
    user_input = input("Enter your HR-related query: ")
    print(f"\nUser: {user_input}")
    result = await Runner.run(triage_agent, user_input)
    print(f"Agent: {result.final_output}")

if __name__ == "__main__":
    asyncio.run(main())