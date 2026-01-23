import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from utils.logger import get_logger

load_dotenv()
logger = get_logger("TTS")

_eleven_client = None

def get_client():
    global _eleven_client
    if _eleven_client is None:
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise RuntimeError("Missing ELEVENLABS_API_KEY in .env")
        _eleven_client = ElevenLabs(api_key=api_key)
        logger.info("ElevenLabs SDK client initialized")
    return _eleven_client

def text_to_speech(text, voice):
    """
    Convert text to speech using the official ElevenLabs Python SDK.
    """
    logger.info(f"TTS request for text: {text[:50]}... with voice: {voice}")
    
    try:
        # Stable method for v2.x SDK
        # We use a default voice ID if 'voice' is a name and not found, 
        # but the SDK also accepts some specific names or IDs.
        # Note: If 'voice' is 'Rachel', the SDK often needs the actual voice_id.
        audio = get_client().text_to_speech.convert(
            voice_id=voice,
            text=text,
            model_id="eleven_turbo_v2"
        )
        
        # The result from convert() is a generator/iterator of bytes in some versions, 
        # or raw bytes. We'll join them if needed.
        if hasattr(audio, '__iter__') and not isinstance(audio, (bytes, bytearray)):
            return b"".join(audio)
        return audio
    except Exception as e:
        logger.error(f"ElevenLabs TTS (SDK) failed: {e}")
        raise
    except Exception as e:
        logger.error(f"ElevenLabs TTS (SDK) failed: {e}")
        raise





# http requests version

# import os
# import requests
# from dotenv import load_dotenv
# from utils.logger import get_logger

# logger = get_logger("TTS")

# _elevenlabs_api_key = None

# def text_to_speech(text: str, voice_id: str = "EXAVITQu4vr4xnSDxMaL"):
#     """
#     Converts text to speech using ElevenLabs API.
#     Lazy loads the API key only on first call.
#     """
#     global _elevenlabs_api_key

#     if _elevenlabs_api_key is None:
#         _elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
#         if not _elevenlabs_api_key:
#             raise RuntimeError("Missing ELEVENLABS_API_KEY in .env")

#     logger.info(f"ElevenLabs TTS request: {text[:50]}...")

#     url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
#     headers = {
#         "xi-api-key": _elevenlabs_api_key,
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "text": text,
#         "model_id": "eleven_monolingual_v1",
#         "voice_settings": {
#             "stability": 0.5,
#             "similarity_boost": 0.7
#         }
#     }

#     try:
#         response = requests.post(url, json=payload, headers=headers)
#         response.raise_for_status()
#         return response.content
#     except Exception as e:
#         logger.error(f"ElevenLabs TTS failed: {e}")
#         raise
