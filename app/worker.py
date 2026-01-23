# worker.py


import base64
from utils.logger import get_logger

# Our separate wrapper modules

import stt.whisper as whisper
import llm.llama as llama
import tts.router as router
import utils.memory as memory
from utils.format_text import clean_text_for_tts as clean_text

logger = get_logger("WORKER")

def process_stt(audio_bytes):
    """Step 1: Convert speech to text."""
    try:
        user_text = whisper.speech_to_text(audio_bytes)
        logger.info(f"STT complete: {user_text[:50]}...")
        return {"user_text": user_text}
    except Exception as e:
        logger.error(f"STT failed: {e}")
        raise

def process_ai_response(user_text, voice="Rachel", session_id="default"):
    """Step 2: LLM + TTS + Memory."""
    try:
        logger.info(f"Starting AI response step | voice: {voice} | session: {session_id}")

        # Add user text to history
        memory.add_to_history(session_id, "user", user_text) 
        # Get context window
        messages = memory.get_messages_for_llm(session_id, max_messages=10)
        
        # A) Generate response
        ai_text = llama.generate_response(messages)
        
        # Add AI response to history
        memory.add_to_history(session_id, "assistant", ai_text)
        
        logger.info(f"Assistant response: {ai_text[:50]}...")

        # B) Text-to-Speech (Clean text first for a more natural voice)
        clean_audio_text = clean_text(ai_text)
        audio_bytes = router.synthesize(clean_audio_text, voice)
        
        return {
            "assistant_text": clean_audio_text,
            "audio_base64": base64.b64encode(audio_bytes).decode("utf-8")
        }
    except Exception as e:
        logger.error(f"AI response step failed: {e}")
        raise















#--------- text & audio input ----------##

# def process_voice_input(audio_bytes):
#     user_text = whisper.speech_to_text(audio_bytes)
#     return process_text_input(user_text)


# def process_text_input(user_text):
#     ai_text = llama.generate_response(user_text)
#     audio_bytes = elevenlabs.text_to_speech(ai_text)

#     return {
#         "user_text": user_text,
#         "assistant_text": ai_text,
#         "audio_base64": base64.b64encode(audio_bytes).decode("utf-8")
#     }
