

import os
import base64
from dotenv import load_dotenv
from groq import Groq
from utils.logger import get_logger

load_dotenv()

groq_client = None 

logger = get_logger("STT")

def speech_to_text(audio_bytes):
    """
    Converts raw audio bytes to text using Groq-hosted Whisper.
    
    Args:
        audio_bytes (bytes): Raw audio data (wav, mp3, etc.)
    
    Returns:
        str: Transcribed text or error message
    """
    logger.info("Starting transcription using Groq Whisper")

    global groq_client

    if groq_client is None:
       groq_api_key = os.getenv("GROQ_API_KEY")
       if not groq_api_key:
            raise RuntimeError("Missing GROQ_API_KEY in .env")
       groq_client = Groq(api_key=groq_api_key)
    
    try:
        response = groq_client.audio.transcriptions.create(
            file=("audio.wav", audio_bytes),
            model="whisper-large-v3"
        )
        transcribed_text = response.text.strip()
        logger.info(f"Transcription successful: {transcribed_text[:50]}...")
        return transcribed_text

    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        raise
