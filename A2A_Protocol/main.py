import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

from agents_server.executors.travel_executor import TravelExecutor
from dotenv import load_dotenv

load_dotenv() 

flight_skill = AgentSkill(
    id="book_flight",
    name="Book Flight",
    description="Books flights between cities",
    tags=["flight", "travel"],
)

hotel_skill = AgentSkill(
    id="book_hotel",
    name="Book Hotel",
    description="Books hotels in a city",
    tags=["hotel", "travel"],
)

cab_skill = AgentSkill(
    id="book_cab",
    name="Book Cab",
    description="Books cabs for travel",
    tags=["cab", "transport"],
)


agent_card = AgentCard(
    name="Travel Services Agent Server",
    description="Handles flight, hotel and cab bookings",
    url="http://localhost:9999/",
    version="1.0.0",
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities=AgentCapabilities(streaming=True),
    skills=[flight_skill, hotel_skill, cab_skill],
)


# request handler
request_handler = DefaultRequestHandler(
    agent_executor=TravelExecutor(),
    task_store=InMemoryTaskStore(),
)


# server
server = A2AStarletteApplication(
    agent_card=agent_card,
    http_handler=request_handler
)


if __name__ == "__main__":
    uvicorn.run(server.build(), host="0.0.0.0", port=9999)