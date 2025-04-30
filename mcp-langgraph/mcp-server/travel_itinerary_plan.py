from typing import Dict, List, Any
from pydantic import BaseModel
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(title="Travel")

# Input model for planning
class PlanRequest(BaseModel):
    """
    Request model for planning a travel itinerary.

    Attributes:
    - days (int): Number of days the user wants the itinerary for.
    - preferences (Dict[str, List[str]]): Optional user preferences, such as preferred activities (e.g., beaches, adventure).
    """
    days: int
    preferences: Dict[str, List[str]] = {}  # e.g. {"activities": ["beach", "adventure"]}

# Output model for itinerary
class Itinerary(BaseModel):
    """
    Represents a day's plan in the travel itinerary.

    Attributes:
    - day (int): The day number in the trip.
    - activities (List[str]): List of activities planned for that day.
    """
    day: int
    activities: List[str]

# Common helper to balance activities
def _build_daily_plan(destination: str, day: int, prefs: Dict[str, List[str]]) -> List[str]:
    """
    Internal helper function to generate a list of activities for a given day based on destination and user preferences.

    Args:
    - destination (str): The travel destination (e.g., 'thailand', 'dubai', 'bali').
    - day (int): The current day number in the itinerary.
    - prefs (Dict[str, List[str]]): User preferences for types of activities.

    Returns:
    - List[str]: A list of 2-3 activities planned for the day, prioritizing preferred activities if possible.
    """
    # base activity pools per destination
    pool = {
        "thailand": [
            "Visit Grand Palace", "Boat ride on Chao Phraya River", "Street food tour",
            "Beach time at Phuket", "Elephant sanctuary visit", "Night market stroll"
        ],
        "dubai": [
            "Burj Khalifa observation deck", "Desert safari", "Dubai Mall shopping",
            "Dubai Fountain show", "Marina yacht cruise", "Old Dubai souk tour"
        ],
        "bali": [
            "Sunrise at Mount Batur", "Tegalalang rice terraces", "Beach day at Kuta",
            "Ubud monkey forest", "Waterfall hike", "Temples of Uluwatu"
        ],
    }
    choices = pool[destination]

    # prioritize any preferred activities
    preferred = prefs.get("activities", [])
    day_plan = []

    # slot 1: if any preferred activity matches pool, pick one
    for act in choices:
        if any(pref.lower() in act.lower() for pref in preferred):
            day_plan.append(act)
            break

    # fill remaining slots by simple rotation
    idx = (day - 1) % len(choices)
    while len(day_plan) < 3:
        candidate = choices[(idx + len(day_plan)) % len(choices)]
        if candidate not in day_plan:
            day_plan.append(candidate)
    return day_plan

# Tool 1: Thailand
@mcp.tool()
async def plan_thailand(request: PlanRequest):
    """
    Generate a detailed multi-day travel itinerary for Thailand.

    Args:
    - request (PlanRequest): 
        - days: Number of days to plan for.
        - preferences: Optional user preferences like type of activities they enjoy.

    Returns:
    - List[Itinerary]: A list containing the day-by-day plan with 2-3 activities per day.
    """
    itinerary = []
    for d in range(1, request.days + 1):
        acts = _build_daily_plan("thailand", d, request.preferences)
        itinerary.append(Itinerary(day=d, activities=acts))
    return itinerary

# Tool 2: Dubai
@mcp.tool()
async def plan_dubai(request: PlanRequest):
    """
    Generate a detailed multi-day travel itinerary for Dubai.

    Args:
    - request (PlanRequest): 
        - days: Number of days to plan for.
        - preferences: Optional user preferences like type of activities they enjoy.

    Returns:
    - List[Itinerary]: A list containing the day-by-day plan with 2-3 activities per day.
    """
    itinerary = []
    for d in range(1, request.days + 1):
        acts = _build_daily_plan("dubai", d, request.preferences)
        itinerary.append(Itinerary(day=d, activities=acts))
    return itinerary

# Tool 3: Bali
@mcp.tool()
async def plan_bali(request: PlanRequest):
    """
    Generate a detailed multi-day travel itinerary for Bali.

    Args:
    - request (PlanRequest): 
        - days: Number of days to plan for.
        - preferences: Optional user preferences like type of activities they enjoy.

    Returns:
    - List[Itinerary]: A list containing the day-by-day plan with 2-3 activities per day.
    """
    itinerary = []
    for d in range(1, request.days + 1):
        acts = _build_daily_plan("bali", d, request.preferences)
        itinerary.append(Itinerary(day=d, activities=acts))
    return itinerary

if __name__ == "__main__":
    import asyncio
    asyncio.run(mcp.run(transport="stdio"))

