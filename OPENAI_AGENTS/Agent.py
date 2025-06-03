import openai
from dataclasses import dataclass
from typing import List, Dict, Optional,Any
from agents import Agent, AgentHooks, Runner, function_tool
from agents import  GuardrailFunctionOutput,InputGuardrailTripwireTriggered,input_guardrail,InputGuardrail
from pydantic import BaseModel
# from agents.lifecycle import RunContextWrapper
from agents.run_context import RunContextWrapper,TContext
from agents.tool import Tool
import os
from dotenv import load_dotenv

load_dotenv()

# openai.api_key = os.getenv("OPENAI_API_KEY")

# --------------------- Step 1: Define User Context ---------------------

@dataclass
class UserContext:
    uid: str
    preferred_language: str
    interests: List[str]
    budget: float

    async def fetch_weather(self, city: str) -> str:
        """
        Fetch the weather for a given city.
        Uses user preferences as part of the response.
        """
        return f"Hello user {self.uid}, the weather in {city} is sunny. The language preferred in the {city} is {self.preferred_language}."

    async def fetch_places_of_interest(self, city: str) -> List[str]:
        """
        Fetch places of interest in a given city.
        Takes into account user interests.
        """
        return [
            f"{interest.title()} Museum in {city}" for interest in self.interests
        ] + [f"Budget tip: Explore free parks in {city}. Your budget is ${self.budget}."]

    async def fetch_activities(self, city: str) -> List[str]:
        """
        Fetch activities based on user interests in a given city.
        """
        return [
            f"Try a {interest}-related activity in {city}" for interest in self.interests
        ] + [f"Budget: {self.budget}, language: {self.preferred_language}"]

# --------------------- Step 2: Define Hooks ---------------------

class MyHooks(AgentHooks):
    async def on_start(self,context: RunContextWrapper[TContext], agent: Agent[TContext]) -> None:
        print(f"🚀 Agent started for user {context}")#.raw_context.uid}.")

    async def on_end(self,context: RunContextWrapper[TContext], agent: Agent[TContext], output: Any) -> None:
        print(f"✅ Agent finished. Final output: {output}")

    async def on_tool_start(self,context: RunContextWrapper[TContext], agent: Agent[TContext], tool: Tool) -> None:
        print(f"🔧 Using tool: {tool.name}")

    async def on_tool_end(self,context: RunContextWrapper[TContext], agent: Agent[TContext], tool: Tool, result: str) -> None:
        print(f"✅ Tool {tool.name} completed. Result: {result}")

# --------------------- Step 3: Define Tools (call context methods) ---------------------

@function_tool
async def get_weather(context: RunContextWrapper[UserContext], city: str) -> str:
    """
    Get the weather for a given city.
    This tool calls the fetch_weather method of UserContext."""
    print("tool get_weather called")
    return await context.context.fetch_weather(city)

@function_tool
async def find_places_of_interest(context: RunContextWrapper[UserContext], city: str) -> List[str]:
    """Find places of interest in a given city.
    This tool calls the fetch_places_of_interest method of UserContext."""
    print("tool find_places_of_interest called")
    return await context.context.fetch_places_of_interest(city)

@function_tool
async def recommend_activities(context: RunContextWrapper[UserContext], city: str) -> List[str]:
    """Recommend activities based on user interests in a given city.
    This tool calls the fetch_activities method of UserContext."""
    print("tool recommend_activities called")
    return await context.context.fetch_activities(city)

class TravelOutput(BaseModel):
    is_travel_related: bool
    reasoning: str

guardrail_agent = Agent(
    name="GuardrailAgent",
    instructions="Check if the user is asking about weather realted, travel-related queries , activities recommended .",
    output_type=TravelOutput,
)

# @input_guardrail
async def travel_guardrail(
    ctx: RunContextWrapper[UserContext],
    agent: Agent,
    input: str
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input=input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=not result.final_output.is_travel_related,
    )

# --------------------- Step 4: Define Agents ---------------------

weather_agent = Agent[UserContext](
    name="WeatherAgent",
    instructions="Provide weather updates by using tools. Pls do not answer on your own, Use tools always. While responding, consider the user id, user's preferences like language and budget.",
    tools=[get_weather],
    # hooks=MyHooks()
)

places_agent = Agent[UserContext](
    name="PlacesAgent",
    instructions="Recommend places of interest by using tools. Pls do not answer on your own, Use tools always.",
    tools=[find_places_of_interest],
    hooks=MyHooks()
)

activities_agent = Agent[UserContext](
    name="ActivitiesAgent",
    instructions="Suggest activities based on interests by using tools. Pls do not answer on your own, Use tools always.",
    tools=[recommend_activities],
    hooks=MyHooks()
)

triage_agent = Agent[UserContext](
    name="TriageAgent",
    instructions="You are a triage agent that routes queries to appropriate sub-agents based on the user's context. If the user asks about the weather, route to WeatherAgent. If they ask about places of interest, route to PlacesAgent. If they ask about activities, route to ActivitiesAgent.",
    handoff_description="Route queries to the appropriate agent based on the user's context.",
    handoffs=[weather_agent, places_agent, activities_agent],
    # input_guardrails=travel_guardrail,
    input_guardrails=[
        InputGuardrail(guardrail_function=travel_guardrail),
    ],
    # hooks=MyHooks()
)


# --------------------- Step 5: Run the Agent ---------------------

import asyncio

async def run_agent():
    user_context = UserContext(
        uid="123",
        preferred_language="English",
        interests=["history", "nature"],
        budget=1000.0
    )
    input_query = input("Enter your query: ")
    result = await Runner.run(triage_agent, input=input_query, context=user_context)
    # result = await Runner.run(triage_agent, input="What part of india is hyderabad", context=user_context)
    print(f"\n🎯 Final Output: {result.final_output}")

asyncio.run(run_agent())
