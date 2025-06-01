import asyncio
import sqlite3
import numpy as np
import sounddevice as sd
import os
from dotenv import load_dotenv
from agents import Agent, Runner, InputGuardrail, GuardrailFunctionOutput, function_tool
from agents.voice import AudioInput, SingleAgentVoiceWorkflow, VoicePipeline
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
from pydantic import BaseModel
import dateparser

load_dotenv()

# -------------------- DB SETUP --------------------
# conn = sqlite3.connect("interviews.db")
# c = conn.cursor()
# c.execute("""
#     CREATE TABLE IF NOT EXISTS interviews (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         candidate TEXT NOT NULL,
#         date TEXT NOT NULL
#     )
# """)
# conn.commit()

# -------------------- TOOLS --------------------
@function_tool
def check_availability(date: str) -> str:
    conn = sqlite3.connect("interviews.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM interviews WHERE date = ?", (date,))
    count = c.fetchone()[0]
    if count >= 3:
        return f"No availability on {date}. Please choose another date."
    return f"{date} is available for interview scheduling."

@function_tool
def book_interview(candidate: str, date: str) -> str:
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
    instructions=prompt_with_handoff_instructions("Respond politely to HR-related queries and route to appropriate agent."),
    handoffs=[availability_agent, booking_agent],
    input_guardrails=[InputGuardrail(guardrail_function=hr_guardrail)],
    model="gpt-4o-mini"
)

# -------------------- VOICE DRIVER --------------------
async def main():
    pipeline = VoicePipeline(workflow=SingleAgentVoiceWorkflow(triage_agent))
    duration = 5  # seconds
    sample_rate = 24000

    print("🎤 Speak your HR query now...")
    mic_audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.int16)
    sd.wait()
    print("✅ Recording done.")

    buffer = mic_audio.flatten()
    audio_input = AudioInput(buffer=buffer)

    result = await pipeline.run(audio_input)

    # Playback result
    player = sd.OutputStream(samplerate=24000, channels=1, dtype=np.int16)
    player.start()

    async for event in result.stream():
        if event.type == "voice_stream_event_audio":
            player.write(event.data)

if __name__ == "__main__":
    asyncio.run(main())
