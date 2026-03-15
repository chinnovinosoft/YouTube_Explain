from agents import Agent, function_tool
from dotenv import load_dotenv

load_dotenv() 

@function_tool
async def book_flight(source: str, destination: str):
    return f"Flight booked from {source} to {destination} with airline AI202."


flight_agent = Agent(
    name="Flight Booking Agent",
    instructions="""
You help users book flights.
Always use the book_flight tool to complete the booking.
""",
    tools=[book_flight],
)