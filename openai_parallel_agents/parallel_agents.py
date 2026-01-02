import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool
import time
from agents import function_tool

load_dotenv()

@function_tool
def search_similar_tickets(ticket_text: str) -> dict:
    """
    Simulates searching a historical ticket database
    and returns realistic summary statistics.
    """

    ticket_text_lower = ticket_text.lower()

    if "payment" in ticket_text_lower and "login" in ticket_text_lower:
        return {
            "similar_tickets_found": 12,
            "common_root_causes": [
                "payment reconciliation delay",
                "temporary auth lock after payment update"
            ],
            "average_resolution_time_minutes": 25,
            "escalation_rate": "20%",
            "recommended_team": "billing-support"
        }

    if "login" in ticket_text_lower or "authentication" in ticket_text_lower:
        return {
            "similar_tickets_found": 8,
            "common_root_causes": [
                "password sync issue",
                "auth service degradation"
            ],
            "average_resolution_time_minutes": 40,
            "escalation_rate": "35%",
            "recommended_team": "identity-access"
        }

    return {
        "similar_tickets_found": 3,
        "common_root_causes": ["unknown"],
        "average_resolution_time_minutes": 60,
        "escalation_rate": "50%",
        "recommended_team": "general-support"
    }


intent_agent = Agent(
    name="IntentClassifier",
    instructions=(
        "Read the support ticket and output a structured interpretation of the "
        "customer’s intent (e.g., billing/technical/login/feature_request)."
    ),
)

sentiment_agent = Agent(
    name="SentimentUrgencyAnalyzer",
    instructions=(
        "Analyze the ticket for customer sentiment and urgency. "
        "Return 'sentiment' and 'urgency' (high/medium/low)."
    ),
)

historical_agent = Agent(
    name="HistoricalContextAgent",
    instructions=(
        "Given a support ticket, summarize similar past tickets and how they were resolved."
    ),
    tools=[search_similar_tickets],
)

meta_agent = Agent(
    name="MetaAggregator",
    instructions=(
        "You have outputs from three agents:\n"
        "1) Intent classification\n"
        "2) Sentiment & urgency\n"
        "3) Similar past ticket summaries\n\n"
        "Produce a final structured triage decision: {\n"
        "  'priority': <high/medium/low>,\n"
        "  'assignment': <team/bot/escalate>,\n"
        "  'reasoning': <brief explanation>\n"
        "}."
    ),
)

parallel_agents = [
    intent_agent,
    sentiment_agent,
    historical_agent
]

starts, ends = [], []
async def run_agent(agent, review_text: str):
    agent_name = agent.name
    print(f'Starting agent: {agent_name}')
    start = time.time()
    starts.append((agent_name, start))

    result = await Runner.run(agent, review_text)

    end = time.time()
    ends.append((agent_name, end))
    print(f'Finished agent: {agent_name} in {end - start:.2f} seconds')

    return result

async def run_agents(review_text: str):
    responses = await asyncio.gather(
        *(run_agent(agent, review_text) for agent in parallel_agents)
    )

    labeled_summaries = [
        f"### {resp.last_agent.name}\n{resp.final_output}"
        for resp in responses
    ]

    collected_summaries = "\n".join(labeled_summaries)
    final_summary = await run_agent(meta_agent, collected_summaries)


    print('Final summary:', final_summary.final_output)

    return "Hi"

review_text = """
Subject: Unable to access account after payment

Hi Team,

I made a payment yesterday but now I’m completely locked out of my account.
It keeps saying “authentication failed” even after resetting the password twice.
This is extremely frustrating because I have a client demo in 2 hours.

Please fix this ASAP.

– Rahul
"""

asyncio.get_event_loop().run_until_complete(run_agents(review_text))