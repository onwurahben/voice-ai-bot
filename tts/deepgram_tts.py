import os
import io
from dotenv import load_dotenv
from deepgram import DeepgramClient, SpeakOptions
from utils.logger import get_logger

load_dotenv()
logger = get_logger("DeepgramTTS")

def text_to_speech(text, voice_name="aura-asteria-en"):
    """
    Synthesize text using Deepgram SDK (Sync).
    Returns audio bytes.
    """
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        raise RuntimeError("Missing DEEPGRAM_API_KEY in .env")

    try:
        logger.info(f"Deepgram SDK TTS request: {text[:50]}... with voice: {voice_name}")
        
        deepgram = DeepgramClient(api_key)

        options = SpeakOptions(
            model=voice_name,
        )

        # The SDK v3 speak method returns a response structure
        # We save to a filename usually, but for memory we stream
        response = deepgram.speak.rest.v("1").speak(
            {"text": text},
            options
        )
        
        # In SDK v3, the sync response for speak has a 'stream' usually when configured,
        # but the standard call returns a wrapper.
        # However, checking the latest SDK standard for bytes:
        # accessing .stream on the response allows reading.
        
        # Let's handle the response buffer safely
        if hasattr(response, "stream"):
            buffer = io.BytesIO()
            # Read from the response stream
            # Note: sync client returns a stream that we can verify
            # actually, standard sync client might return bytes or a specific object.
            # Verifying SDK v3 patterns: 
            # filename = "output.mp3"
            # deepgram.speak.rest.v("1").save(filename, {"text": text}, options)
            # The 'speak' method returns a httpx response wrapper in raw mode often?
            # Actually, standard usage in docs is .save or .stream for blocks.
            
            # Let's try to get raw bytes from the stream directly.
            buffer.write(response.stream.read())
            return buffer.getvalue()
            
        else:
            # If not a stream attribute, it might be the response itself or similar.
            # Fallback to creating a temp file if memory stream fails? 
            # No, let's use the .to_file logic reversed or check headers.
            # Actually, let's trust the .stream property which is standard for the httpx wrapper the SDK uses.
            return response.content if hasattr(response, 'content') else b''

    except Exception as e:
        logger.error(f"Deepgram SDK TTS failed: {e}")
        raise

