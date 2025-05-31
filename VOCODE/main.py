import asyncio
import signal

from pydantic_settings import BaseSettings, SettingsConfigDict

from vocode.helpers import create_streaming_microphone_input_and_speaker_output
from vocode.logging import configure_pretty_logging
from vocode.streaming.agent.chat_gpt_agent import ChatGPTAgent
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.synthesizer import AzureSynthesizerConfig
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig,GoogleSynthesizerConfig
from vocode.streaming.models.transcriber import (
    DeepgramTranscriberConfig,
    PunctuationEndpointingConfig,
)
from vocode.streaming.streaming_conversation import StreamingConversation
from vocode.streaming.synthesizer.azure_synthesizer import AzureSynthesizer
from vocode.streaming.transcriber.deepgram_transcriber import DeepgramTranscriber
from vocode.streaming.synthesizer.eleven_labs_synthesizer import ElevenLabsSynthesizer
from vocode.streaming.synthesizer.google_synthesizer import GoogleSynthesizer
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig


configure_pretty_logging()
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "sodium-burner-461507-p5-4d6749a6eab0.json"
class Settings(BaseSettings):
    """
    Settings for the streaming conversation quickstart.
    These parameters can be configured with environment variables.
    """

    openai_api_key: str = ""
    azure_speech_key: str = "ENTER_YOUR_AZURE_KEY_HERE"
    deepgram_api_key: str = ""
    elevenlabs_api_key: str = ""
    azure_speech_region: str = "eastus"

    # This means a .env file can be used to overload these settings
    # ex: "OPENAI_API_KEY=my_key" will set openai_api_key over the default above
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()


async def main():
    (
        microphone_input,
        speaker_output,
    ) = create_streaming_microphone_input_and_speaker_output(
        use_default_devices=True,
        # use_blocking_speaker_output=True,  # this moves the playback to a separate thread, set to False to use the main thread
    )

    conversation = StreamingConversation(
        output_device=speaker_output,
        transcriber=DeepgramTranscriber(
            DeepgramTranscriberConfig.from_input_device(
                microphone_input,
                endpointing_config=PunctuationEndpointingConfig(),
                api_key=settings.deepgram_api_key,
            ),
        ),
        agent=ChatGPTAgent(
            ChatGPTAgentConfig(
                openai_api_key=settings.openai_api_key,
                initial_message=BaseMessage(text="What up"),
                prompt_preamble="""The AI is having a pleasant conversation about life""",
            )
        ),
        # synthesizer=AzureSynthesizer(
        #     AzureSynthesizerConfig.from_output_device(speaker_output),
        #     azure_speech_key=settings.azure_speech_key,
        #     azure_speech_region=settings.azure_speech_region,
        # ),
        # synthesizer = ElevenLabsSynthesizerConfig(
        #     api_key= settings.elevenlabs_api_key
        # )
        # synthesizer=ElevenLabsSynthesizer(
        #     ElevenLabsSynthesizerConfig.from_output_device(
        #         output_device=speaker_output,
        #         api_key=settings.elevenlabs_api_key,
        #         output_format="mp3_44100_192"
        #         # voice_id="Rachel"  # Optional: specify ElevenLabs voice ID
        #     )
        synthesizer=GoogleSynthesizer(
            GoogleSynthesizerConfig.from_output_device(
                output_device=speaker_output,
                language_code="en-US",
                voice_name="en-US-Wavenet-D",
                speaking_rate=1.0,
                pitch=0.0,
            )
)
    )
    await conversation.start()
    print("Conversation started, press Ctrl+C to end")
    signal.signal(signal.SIGINT, lambda _0, _1: asyncio.create_task(conversation.terminate()))
    while conversation.is_active():
        chunk = await microphone_input.get_audio()
        conversation.receive_audio(chunk)


if __name__ == "__main__":
    asyncio.run(main())