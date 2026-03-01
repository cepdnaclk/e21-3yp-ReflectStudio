import sys
import asyncio
import traceback
import os
import pyaudio
import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ================= WINDOWS ASYNCIO FIX =================
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ================= LOAD ENV VARIABLES =================
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file")

# ================= CONFIGURATION =================
MODEL = "models/gemini-2.5-flash-native-audio-preview-12-2025"

CUSTOM_PROMPT = (
    """
You are SinhalaBot, a warm, kind, and respectful Sinhala AI assistant.

You always speak in a calm, gentle, and supportive tone.
You are patient and generous in your explanations.
You encourage the user and make them feel comfortable.

Your personality traits:
- Kind
- Helpful
- Respectful
- Supportive
- Polite
- Calm

You speak natural Sinhala.
Avoid slang or swag language.
Do not use arrogant or overly energetic expressions.
Be soft and friendly.
"""
)

# ================= AUDIO SETTINGS (Windows Safe) =================
FORMAT = pyaudio.paInt16
CHANNELS = 1
HARDWARE_IN_RATE = 44100   # Windows microphones typically use 44.1kHz
HARDWARE_OUT_RATE = 44100  # Gemini native output
CHUNK = 1024

# ================= GEMINI CLIENT =================
client = genai.Client(
    http_options={"api_version": "v1beta"},
    api_key=GEMINI_API_KEY
)

CONFIG = types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Puck"
            )
        )
    ),
)

pya = pyaudio.PyAudio()

# ======================================================
# =================== SINHALA BOT ======================
# ======================================================

class SinhalaBot:
    def __init__(self):
        self.audio_in_queue = None
        self.out_queue = None
        self.session = None
        self.should_exit = False

    async def listen_mic(self):
        """Capture audio from microphone"""
        stream = pya.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=HARDWARE_IN_RATE,
            input=True,
            input_device_index=1,
            frames_per_buffer=CHUNK
            
        )

        stream_out = pya.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=HARDWARE_OUT_RATE,
            output=True,
            output_device_index=1,
            
            
        )


        print("🎤 Listening...")

        while not self.should_exit:
            try:
                data = await asyncio.to_thread(
                    stream.read,
                    CHUNK,
                    exception_on_overflow=False
                )

                audio_array = np.frombuffer(data, dtype=np.int16)

                # Downsample for Gemini (~16kHz target)
                downsampled_data = audio_array[::3].tobytes()

                await self.out_queue.put({
                    "mime_type": "audio/pcm",
                    "data": downsampled_data
                })

            except Exception as e:
                print("Mic Error:", e)

    async def play_speaker(self):
        """Play AI audio response"""
        stream = pya.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=HARDWARE_OUT_RATE,
            output=True
        )

        while not self.should_exit:
            try:
                data = await self.audio_in_queue.get()
                await asyncio.to_thread(stream.write, data)
            except Exception as e:
                print("Speaker Error:", e)

    async def send_loop(self):
        while not self.should_exit:
            msg = await self.out_queue.get()
            await self.session.send(input=msg)

    async def receive_loop(self):
        while not self.should_exit:
            async for response in self.session.receive():
                if response.data:
                    await self.audio_in_queue.put(response.data)

    async def run(self):
        # Create queues INSIDE running loop (fixes Windows issue)
        self.audio_in_queue = asyncio.Queue()
        self.out_queue = asyncio.Queue(maxsize=5)

        async with client.aio.live.connect(model=MODEL, config=CONFIG) as session:
            self.session = session

            # Send persona first
            await self.session.send(
                input=CUSTOM_PROMPT,
                end_of_turn=True
            )

            print("🚀 SinhalaBot is LIVE! Say something in Sinhala...")

            await asyncio.gather(
                self.listen_mic(),
                self.play_speaker(),
                self.receive_loop(),
                self.send_loop()
            )

# ======================================================
# =================== ENTRY POINT ======================
# ======================================================

if __name__ == "__main__":
    bot = SinhalaBot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\n👋 SinhalaBot signing off!")
    except Exception as e:
        print("Unexpected Error:", e)
        traceback.print_exc()
    finally:
        pya.terminate()
