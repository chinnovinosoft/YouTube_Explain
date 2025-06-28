import os
import io
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from openai import OpenAI
from elevenlabs import play
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
from src.hotel_guide.main import kickoff

load_dotenv()

# Load credentials
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

# Init clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
elevenlabs = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def record_user_input(duration=8, fs=24000) -> io.BytesIO:
    print("🎙️ Speak now...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    print("✅ Recording complete.")
    buffer = io.BytesIO()
    write(buffer, fs, recording)
    buffer.seek(0)
    return buffer

def extract_text(audio_buffer: io.BytesIO) -> str:
    audio_buffer.seek(0)
    response = openai_client.audio.transcriptions.create(
        model="whisper-1",
        file=("audio.wav", audio_buffer, "audio/wav"),
    )
    print("📝 Transcription:", response.text)
    return response.text

def generate_audio(text: str) -> io.BytesIO:
    print("🗣️ Speaking the response...")
    audio = elevenlabs.text_to_speech.convert(
        text=text,
        voice_id=ELEVENLABS_VOICE_ID,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    play(audio)
    return audio

def main():
    audio_buf = record_user_input()
    text = extract_text(audio_buf)
    response = kickoff(text)
    generate_audio(response)

if __name__ == "__main__":
    main()
