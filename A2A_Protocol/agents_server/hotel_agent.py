from agents import Agent, function_tool
from dotenv import load_dotenv

load_dotenv() 

@function_tool
async def book_hotel(city: str):
    return f"Hotel booked in {city} at SeaView Resort."


hotel_agent = Agent(
    name="Hotel Booking Agent",
    instructions="""
You help users book hotels.
Use the book_hotel tool when a hotel booking is requested.
""",
    tools=[book_hotel],
)