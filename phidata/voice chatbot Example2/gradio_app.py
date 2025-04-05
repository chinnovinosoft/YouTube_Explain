import os
from dotenv import load_dotenv
import gradio as gr
from io import BytesIO
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from openai import OpenAI
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools import tool
import requests
import psycopg2
import tempfile

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Set up clients
oai_client = OpenAI(api_key=OPENAI_API_KEY)
el_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# DB connection helper
def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="phidata_db",
        user="postgres",
        password="postgres"
    )

# AGNO Tools
@tool(name="get_table_schema", description="Fetches the schema of the table.", show_result=True)
def get_table_schema() -> str:
    conn = get_connection()
    table_name = "vehicle_policies"
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))
            rows = cur.fetchall()
            if not rows:
                return f"No schema found for table '{table_name}'."
            schema_lines = [
                f"{col}: {dtype}({length})" if length else f"{col}: {dtype}"
                for col, dtype, length in rows
            ]
            return "\n".join(schema_lines)
    finally:
        conn.close()

@tool(name="execute_sql", description="Executes SQL and fetches vehicle_policies info", show_result=True)
def execute_sql_query(query: str) -> str:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            if cur.description:
                rows = cur.fetchall()
                return "\n".join(str(row) for row in rows)
            else:
                conn.commit()
                return "Query executed successfully."
    except Exception as e:
        return f"Error executing query: {e}"
    finally:
        conn.close()

@tool(name="fetch_claim_status", description="Gets claim status by ID", show_result=True)
def fetch_claim_status(claim_id):
    claim_id = claim_id.replace(' ','').replace('-','')
    res = requests.post("http://127.0.0.1:8000/claim/status", json={"claim_id": claim_id})
    try:
        data = res.json()
        if "status" in data:
            return "The status of the claim is: " + str(data["status"])
        else:
            return "⚠️ 'status' not found in the API response."
    except Exception as e:
        return f"❌ Failed to parse response: {e}"

@tool(name="fetch_claim_date", description="Gets claim date by ID", show_result=True)
def fetch_claim_date(claim_id):
    claim_id = claim_id.replace(' ','').replace('-','')
    res = requests.post("http://127.0.0.1:8000/claim/date", json={"claim_id": claim_id})
    try:
        data = res.json()
        if "claim_date" in data:
            return "The date the claim was made: " + str(data["claim_date"])
        else:
            return "⚠️ 'claim_date' not found in the API response."
    except Exception as e:
        return f"❌ Failed to parse response: {e}"

@tool(name="fetch_latest_comment_on_claim", description="Gets latest insurer comment", show_result=True)
def fetch_latest_comment_on_claim(claim_id):
    claim_id = claim_id.replace(' ','').replace('-','')
    res = requests.post("http://127.0.0.1:8000/claim/comment", json={"claim_id": claim_id})
    try:
        data = res.json()
        if "latest_comment" in data:
            return "Latest insurer comment: " + str(data["latest_comment"])
        else:
            return "⚠️ 'latest_comment' not found in the API response."
    except Exception as e:
        return f"❌ Failed to parse response: {e}"

# Agents
sql_generator_agent = Agent(
    name="SQL_Query_Generator",
    role="Generates SQL queries",
    model=OpenAIChat(id="gpt-4o"),
    tools=[get_table_schema],
    instructions=[
        "You are an expert SQL query generator. Use schema tools to construct valid queries."
    ],
    show_tool_calls=True,
    markdown=True,
)

sql_exec_agent = Agent(
    name="SQL Executor Agent",
    role="Executes SQL queries and explains the result",
    model=OpenAIChat(id="gpt-4o"),
    tools=[execute_sql_query],
    instructions=[
        "Run SQL queries and return human-readable responses. Don’t mention SQL syntax."
    ],
    show_tool_calls=True,
    markdown=True,
)

api_agent = Agent(
    name="API Trigger Agent",
    role="Handles insurance API queries",
    model=OpenAIChat(id="gpt-4o"),
    tools=[fetch_latest_comment_on_claim, fetch_claim_status, fetch_claim_date],
    instructions=[
        "Understand claim queries and use appropriate tools. Don’t fabricate info."
    ],
    show_tool_calls=True,
    markdown=True,
)

sql_team = Team(
    name="SQL Generator Executor Team",
    mode="coordinate",
    model=OpenAIChat("gpt-4.5-preview"),
    members=[sql_generator_agent, sql_exec_agent],
    show_tool_calls=True,
    markdown=True,
    instructions=[
        "Generate a valid SQL query and execute it. Return only the interpreted result."
    ],
    show_members_responses=True,
)

final_team = Team(
    name="User Query Response Team",
    mode="route",
    model=OpenAIChat("gpt-4.5-preview"),
    members=[sql_team, api_agent],
    show_tool_calls=True,
    markdown=True,
    instructions=[
        "Classify the query and route to either SQL team or API agent appropriately."
    ],
    show_members_responses=True,
)

# Text-to-Speech
def text_to_speech_stream(text: str) -> BytesIO:
    response = el_client.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB",  # Adam
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
            speed=1.0,
        ),
    )
    audio_stream = BytesIO()
    for chunk in response:
        if chunk:
            audio_stream.write(chunk)
    audio_stream.seek(0)
    return audio_stream

# Main chat function
def voice_chat(audio_path):
    # Step 1: Transcribe
    with open(audio_path, "rb") as f:
        transcript = oai_client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
    text_input = transcript.text
    print("text_input --> ", text_input.replace('-',''))

    # Step 2: Run agent
    res = final_team.run(text_input.replace('-',''))
    response_text = res.content
    print("response we got is -->",response_text)

    # Step 3: Text-to-speech
    audio_stream = text_to_speech_stream(response_text)

    # Step 4: Save to file for Gradio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tmp_file.write(audio_stream.read())
        audio_path = tmp_file.name

    return response_text, audio_path

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## 🎙️ Voice-based Insurance Chatbot\nAsk anything about your policy or claim")

    with gr.Row():
        audio_input = gr.Audio(type="filepath", label="🎤 Speak your query", format="wav")
        response_text = gr.Textbox(label="📜 Agent's Response")
        audio_output = gr.Audio(label="🔊 Response Audio")

    submit_btn = gr.Button("🟢 Ask")
    submit_btn.click(fn=voice_chat, inputs=audio_input, outputs=[response_text, audio_output])

demo.launch()
