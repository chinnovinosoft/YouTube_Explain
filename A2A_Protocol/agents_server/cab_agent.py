from agents import Agent, function_tool
from dotenv import load_dotenv

load_dotenv() 


@function_tool
async def book_cab(city: str):
    return f"Cab booked in {city} for airport pickup."
    

cab_agent = Agent(
    name="Cab Booking Agent",
    instructions="""
You arrange cab transportation.
Use the book_cab tool to complete bookings.
""",
    tools=[book_cab],
)