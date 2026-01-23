import os
from .google_tts import text_to_speech as google_tts
# Rename deepgram_tts import to match probable filename or fix filename later; user router had .deepgram_tts
from .deepgram_tts import text_to_speech as deepgram_tts
from .elevenlabs import text_to_speech as elevenlabs_tts
from dotenv import load_dotenv

load_dotenv()

TTS_PROVIDER = os.getenv("TTS_PROVIDER", "google").lower()

# Central Voice Map
VOICE_MAP = {
    "Rachel": {
        "elevenlabs": "21m00Tcm4TlvDq8ikWAM",  # Rachel
        "deepgram": "aura-asteria-en",         # Asteria (Female)
        "google": "en-US-Journey-F"            # Journey-F (Female)
    },
    "Clyde": {
        "elevenlabs": "2EiwWnXFnvU5JabPnv8n",  # Clyde
        "deepgram": "aura-orion-en",           # Orion (Male)
        "google": "en-US-Standard-D"           # Standard-D (Male)
    },
    "Mimi": {
        "elevenlabs": "zrHiDhphv9ZnVXBqCLjf",  # Mimi
        "deepgram": "aura-luna-en",            # Luna (Female/Young)
        "google": "en-US-Standard-A"           # Standard-A (Female)
    }
}

DEFAULT_VOICES = {
    "elevenlabs": "21m00Tcm4TlvDq8ikWAM",
    "deepgram": "aura-asteria-en",
    "google": "en-US-Journey-F"
}

def synthesize(text, voice_name="Rachel"):
    """
    Unified TTS interface.
    Maps generic voice_name (Rachel/Clyde/Mimi) to provider-specific ID.
    Returns audio bytes.
    """
    # 1. Resolve Provider ID
    provider_map = VOICE_MAP.get(voice_name)
    
    if provider_map and TTS_PROVIDER in provider_map:
        voice_id = provider_map[TTS_PROVIDER]
    else:
        # Fallback to default if voice not found or provider not in map
        voice_id = DEFAULT_VOICES.get(TTS_PROVIDER)

    # 2. Call Provider
    if TTS_PROVIDER == "google":
        return google_tts(text, voice_id)

    if TTS_PROVIDER == "deepgram":
        return deepgram_tts(text, voice_id)

    if TTS_PROVIDER == "elevenlabs":
        return elevenlabs_tts(text, voice_id)

    raise ValueError(f"Unsupported TTS provider: {TTS_PROVIDER}")
