import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()
api_key = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=api_key)

try:
    response = client.voices.get_all()
    with open("voices.txt", "w", encoding='utf-8') as f:
        for voice in response.voices:
            f.write(f"{voice.name}|{voice.voice_id}\n")
    print("Voices saved to voices.txt")
except Exception as e:
    print(f"Error: {e}")
