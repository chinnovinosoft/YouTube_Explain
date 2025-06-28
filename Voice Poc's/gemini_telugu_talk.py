import google.genai as genai 
from google.genai import types 
import os
import pyaudio
import wave
from pydub import AudioSegment
from pydub.playback import play
import io
import asyncio
import struct
from dotenv import load_dotenv

load_dotenv()  

API_KEY = ""

if not API_KEY:
    raise ValueError("Please set the GOOGLE_API_KEY environment variable.")

# Initialize the new genai client with the API key
client = genai.Client(api_key=API_KEY)

# --- Audio Recording Parameters ---
FORMAT = pyaudio.paInt16  # 16-bit resolution
CHANNELS = 1              # Mono audio
RATE = 16000              # Sample rate: 16kHz (common for speech)
CHUNK = 1024              # Number of frames per buffer
RECORD_SECONDS = 5        # Record for 5 seconds

# --- Gemini Model Names ---
# For audio input (speech-to-text) and text generation:
SPEECH_TO_TEXT_MODEL = "gemini-1.5-flash" 

# For text-to-speech (native audio output):
TEXT_TO_SPEECH_MODEL = "gemini-2.5-flash-preview-tts" 

# --- Helper function to play audio bytes ---
def play_audio_bytes(audio_bytes, sample_width=2, frame_rate=24000, channels=1):
    """
    Plays raw L16 PCM audio bytes.
    Assumes 16-bit PCM, 24kHz, mono for Gemini TTS output.
    """
    try:
        if not AudioSegment.converter or not AudioSegment.ffmpeg:
            print("Warning: pydub's playback backend (simpleaudio or ffmpeg) might not be configured.")
            print("Attempting to play, but if it fails, ensure simpleaudio is installed (`pip install simpleaudio`)")
            print("or ffmpeg is in your system's PATH.")

        audio = AudioSegment(
            data=audio_bytes,
            sample_width=sample_width,
            frame_rate=frame_rate,
            channels=channels
        )
        print("Playing Gemini's response...")
        play(audio)
        print("Audio playback finished.")
    except Exception as e:
        print(f"Error playing audio: {e}")
        print("Ensure 'simpleaudio' (for pydub backend) is correctly installed and your audio drivers are working.")

# --- Function to record audio from microphone to an in-memory buffer ---
def record_audio_to_buffer(duration_seconds=RECORD_SECONDS):
    print(f"\nRecording audio for {duration_seconds} seconds...")
    audio_api = pyaudio.PyAudio() 
    stream = audio_api.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    frames = []
    for _ in range(0, int(RATE / CHUNK * duration_seconds)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording finished.")

    stream.stop_stream()
    stream.close()
    audio_api.terminate()

    full_audio_bytes = b''.join(frames)

    # Create an in-memory WAV file
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio_api.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(full_audio_bytes)
    
    # Rewind the buffer to the beginning for reading
    buffer.seek(0)
    
    print(f"Recorded audio stored in memory buffer (total {len(full_audio_bytes)} bytes raw PCM).")
    return buffer, full_audio_bytes 

# --- Function to send audio buffer to Gemini for STT and text generation ---
async def process_audio_input_with_gemini(audio_buffer_io):
    print(f"\n--- Sending audio to Gemini for transcription and understanding ---")
    try:
        # Directly call generate_content on client.models and pass model as a keyword argument
        response = client.models.generate_content(
            model=SPEECH_TO_TEXT_MODEL, # Pass model as keyword argument
            contents=[
                # Correct way to pass audio data using inline_data dictionary
                {
                    "inline_data": {
                        "mime_type": "audio/wav",
                        "data": audio_buffer_io.getvalue()
                    }
                },
                # Prompt the model to respond to questions in Telugu with short answers.
                {"text": "ఈ తెలుగు ఆడియో సందేశంలోని ప్రశ్నలకు తెలుగులో సంక్షిప్త సమాధానాలు ఇవ్వండి. (Give short answers in Telugu to the questions in this Telugu audio message.)"}
            ]
        )
        
        # Check if the response contains text
        if response.text:
            print(f"Gemini's understanding (text): {response.text}")
            return response.text
        else:
            print("Gemini did not return a text response for the audio input.")
            return None

    except Exception as e:
        print(f"Error processing audio with Gemini: {e}")
        return None


# --- Function to generate Telugu speech from Gemini's text response ---
async def generate_telugu_speech_from_text(text_to_speak):
    print(f"\n--- Generating Telugu speech response ---")
    try:
        response = client.models.generate_content(
            model=TEXT_TO_SPEECH_MODEL,
            contents=text_to_speak,
            config=types.GenerateContentConfig( 
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name='Kore', 
                        )
                    )
                ),
            )
        )

        audio_parts = []
        if response.candidates:
            for candidate in response.candidates:
                if candidate.content and candidate.content.parts: # Also check content and parts
                    for part in candidate.content.parts:
                        if part.inline_data:
                            audio_parts.append(part.inline_data.data)
                        elif part.file_data:
                            print(f"Received file data URI: {part.file_data.file_uri}")
        
        if audio_parts:
            full_audio_bytes = b''.join(audio_parts)
            play_audio_bytes(full_audio_bytes, frame_rate=24000) # Gemini TTS is 24kHz
        else:
            print("No audio data received in Gemini's response.")

    except Exception as e:
        print(f"Error generating Telugu speech from text: {e}")

# --- Main conversational loop ---
async def main():

    try:
        audio_buffer_io, _ = record_audio_to_buffer(RECORD_SECONDS) # We only need the BytesIO object
        gemini_text_response = await process_audio_input_with_gemini(audio_buffer_io)
        print(f"Gemini's text response: {gemini_text_response}")

        if gemini_text_response:
            await generate_telugu_speech_from_text(gemini_text_response)
        else:
            print("Could not get a meaningful text response from Gemini.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print("Please try again.")

if __name__ == "__main__":
    asyncio.run(main())
