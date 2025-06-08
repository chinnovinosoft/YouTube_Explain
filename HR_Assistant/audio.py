import os
from io import BytesIO
from typing import List
import sounddevice as sd
from scipy.io.wavfile import write
from elevenlabs.client import ElevenLabs
from langchain_core.messages import HumanMessage, AIMessage, AnyMessage
from langgraph.graph.message import add_messages
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.prebuilt import create_react_agent
from openai import OpenAI
import simpleaudio as sa
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from elevenlabs import play
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import json 


load_dotenv()
elevenlabs = ElevenLabs(
  api_key=os.getenv("ELEVENLABS_API_KEY"),
)

llm = ChatOpenAI(model="gpt-4o-mini")

class UserDetails(BaseModel):
    """User's personal details extracted from their response."""
    full_name: str = Field(description="The user's full name")
    email: str = Field(description="The user's email address")
    phone_number: str = Field(description="The user's phone number")

def generate_audio(text: str, model: str = "eleven_multilingual_v2") -> BytesIO:
    """
    Generate audio from text using ElevenLabs API.
    """
    audio = elevenlabs.text_to_speech.convert(
        text=text,
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id=model,
        output_format="mp3_44100_128",
    )
    play(audio)

# def play_audio(audio_buffer: BytesIO):
#     """
#     Play audio from a BytesIO buffer.
#     """
#     audio_buffer.seek(0)
#     wave_obj = sa.WaveObject.from_wave_file(audio_buffer)
#     play_obj = wave_obj.play()
#     play_obj.wait_done()

def record_user_input(duration: int = 10, fs: int = 44100) -> BytesIO:
    """
    Record audio from the user's microphone and return it as a BytesIO buffer (WAV format).
    """
    print("Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    buffer = BytesIO()
    write(buffer, fs, recording)
    buffer.seek(0)
    return buffer

def extract_text(audio_buffer: BytesIO) -> str:
    """
    Transcribe an audio file to text using OpenAI's GPT-4o model.
    """
    client = OpenAI()
    try:
        audio_buffer.seek(0)
        transcription = client.audio.transcriptions.create(
            model="whisper-1",  # GPT-4o uses whisper-1 API for transcriptions
            file=("audio.wav", audio_buffer)
        )
        return transcription.text
    except Exception as e:
        raise Exception(f"Error during transcription: {e}")

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    agent_queries: list[str]
    user_details: list[dict[str, str]]
    tech_stack_details: Optional[list[dict[str, str]]] = None

def speak_and_listen(agent_prompt: str,record_duration=10) -> str:
    """
    Generate agent audio, play it, record user response, and transcribe.
    """
    # Generate agent audio
    print(f"Agent Prompt: {agent_prompt}")
    audio = generate_audio(agent_prompt)
    # Record user response
    user_audio = record_user_input(record_duration)
    # Transcribe user response
    user_text = extract_text(user_audio)
    print(f"User: {user_text}")
    return user_text

def greet_node(state: State) -> State:
    """
    Greet the user and return a greeting message using a dynamic agent response.
    """
    prompt="You are a HR Agent, Inform that you are HR Agent. Greet the user and ask if they are looking for a job change in the 'Data Engineering' Role. Be friendly, crisp and short, do not give a lengthy greeting. Never say 'How can I assist you ?'. You are a HR Agent and asking just if they are looking for a job change. "
    res = llm.invoke([HumanMessage(content=prompt)])
    # Add agent's message to state
    state["messages"].append(AIMessage(content=res.content))
    # Speak and listen using the agent's response
    user_response = speak_and_listen(res.content,record_duration=3)  # Adjust duration as needed
    # Add user response to state
    state["messages"].append(HumanMessage(content=user_response))
    print("state[messages] in greet node --> ",state["messages"])
    return {'messages': state['messages']}

def gather_personal_details_node(state: State) -> State:
    """
    Gather personal details from the user using a dynamic agent response.
    """
    prompt="You are a HR Agent. Ask the user for their Good Name, Email Address and Phone Number. Be polite. Ask for all details at once."
    # chain = prompt | llm
    # res = chain.invoke(state["messages"])
    res = llm.invoke([HumanMessage(content=prompt)])
    # Add agent's message to state
    state["messages"].append(AIMessage(content=res.content))
    # Speak and listen using the agent's response
    user_response = speak_and_listen(res.content)
    # Add user response to state
    state["messages"].append(HumanMessage(content=user_response))
    print("state[messages] in gather personal details node --> ",state["messages"])
    user_info_prompt = "Extract the user's Full Name, Email Address and Phone Number from the following text "
    user_info_prompt += f"User Response: {user_response}"
    # Use LLM to extract user details
    user_info = llm.with_structured_output(UserDetails).invoke([HumanMessage(content=user_info_prompt)])
    print("Extracted User Details: ", user_info)
    # Add user details to state
    return {'user_details': user_info}

def get_tech_stack():
    with open('tech_required.txt', 'r') as file:
        base = file.read().strip().split('\n')
        tech_required = base[0].split(':')[1]
        cloud_required = base[1].split(':')[1]
        orchestration_required = base[2].split(':')[1]
    print(f"Tech Required: {tech_required}", f"Cloud Required: {cloud_required}", f"Orchestration Required: {orchestration_required}", sep='\n')
    return tech_required, cloud_required, orchestration_required

class TechStackDetails(TypedDict):
    """
    User's technology stack details.
    """
    tech_stack: Annotated[str, ..., "The name of the technology (e.g., Spark)"]
    rating: Annotated[str, ..., "User's self-assessed rating for this technology"]
    explanation: Annotated[str, ..., "User's explanation of their experience with this technology"]

class TechStackDetailsList(BaseModel):
    items: List[TechStackDetails] = Field(
        description="List of technology stack details provided by the user."
    )

def fetch_user_tech_stack_node(state: State) -> State:
    """
    Fetch the user's technology stack under Data Engineering.
    """
    tech_required, cloud_required, orchestration_required = get_tech_stack()

    # 1. Ask LLM to generate 3 questions, one for each section
    prompt = (
        "You are a HR Agent. For each of the following technology sections, generate a question asking the user if they have experience with the listed technologies, "
        "how they would rate themselves, and any explanation they'd like to add. "
        "Sections:\n"
        f"1. Data Engineering Basics: {tech_required}\n"
        f"2. Cloud (AWS): {cloud_required}\n"
        f"3. Orchestration: {orchestration_required}\n"
        "Return the 3 questions as a list of strings, each question on a new line. "
    )
    llm_questions_res = llm.invoke([HumanMessage(content=prompt)])
    # Assume LLM returns a list of 3 questions as text, parse it
    import ast
    try:
        questions = ast.literal_eval(llm_questions_res.content)
    except Exception:
        # fallback: split by newlines if not a list
        questions = [q.strip() for q in llm_questions_res.content.split('\n') if q.strip()]

    # 2. Iterate over questions, ask user, collect responses
    user_responses = []
    for question in questions:
        response = speak_and_listen(question,record_duration=20)  # Adjust duration as needed
        user_responses.append(response)
    extraction_prompt = (
        "For each technology mentioned in the following user responses, extract the technology name, the user's self-assessed rating, and any explanation. "
        "Return a dictionary with a single key 'items', whose value is a list of dictionaries, each with keys: 'tech_stack', 'rating', 'explanation'. "
        "If the user mentions multiple technologies in one response, create a separate dictionary for each technology. "
        "Responses:\n"
    )
    for idx, (question, response) in enumerate(zip(questions, user_responses), 1):
        extraction_prompt += f"Section {idx} Question: {question}\nUser Response: {response}\n"
        
    tech_stack_details = llm.with_structured_output(TechStackDetailsList).invoke([HumanMessage(content=extraction_prompt)])
    print("Extracted Tech Stack Details: ", tech_stack_details)
    # Add to state
    with open("user_tech_stack.json", "w") as f:
        json.dump(tech_stack_details.dict(), f, indent=2)
    return {"tech_stack_details": tech_stack_details}

def greet_bye(state: State) -> State:
    """
    Greet the user and say goodbye.
    """
    prompt = "You are a HR Agent. Thank the user for their time and say goodbye. Also, inform them that you will reach out to them soon with the next steps. Keep it short and polite."
    res = llm.invoke([HumanMessage(content=prompt)])
    # Add agent's message to state
    state["messages"].append(AIMessage(content=res.content))
    # Speak and listen using the agent's response
    user_response = speak_and_listen(res.content)
    # Add user response to state
    state["messages"].append(HumanMessage(content=user_response))
    print("state[messages] in greet bye node --> ",state["messages"])
    return {'messages': state['messages']}

def build_hr_agent_graph():
    graph = StateGraph(State)
    # Add nodes
    graph.add_node("greet", greet_node)
    graph.add_node("gather_details", gather_personal_details_node)
    graph.add_node("fetch_tech_stack", fetch_user_tech_stack_node)
    graph.add_node("greet_bye", greet_bye)
    # Define edges (flow)
    graph.add_edge("greet", "gather_details")
    graph.add_edge("gather_details", "fetch_tech_stack")
    graph.add_edge("fetch_tech_stack", "greet_bye")
    # You can add more nodes and edges as needed

    # Set entry point
    graph.set_entry_point("greet")
    return graph

# To run the graph:
graph = build_hr_agent_graph()
chain = graph.compile()
chain.invoke(State(messages=[], agent_queries=[], user_responses=[]))