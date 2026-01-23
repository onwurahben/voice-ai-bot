import os
from google.cloud import texttospeech
from utils.logger import get_logger

logger = get_logger("GoogleTTS")

def text_to_speech(text, voice_name="en-US-Journey-F"):
    """
    Synthesize text using Google Cloud TTS.
    Returns audio bytes (MP3).
    
    Requires GOOGLE_APPLICATION_CREDENTIALS environment variable 
    pointing to your Service Account JSON key file.
    """
    try:
        logger.info(f"Google TTS request: {text[:50]}... with voice: {voice_name}")
        
        # Instantiates a client
        client = texttospeech.TextToSpeechClient()

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Build the voice request
        # Assumes voice_name is like "en-US-Standard-C"
        language_code = "-".join(voice_name.split("-")[:2]) # "en-US"
        
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # The response's audio_content is binary.
        return response.audio_content

    except Exception as e:
        logger.error(f"Google TTS failed: {e}")
        # Hint for common error
        if "DefaultCredentialsError" in str(e):
            logger.error("Did you set GOOGLE_APPLICATION_CREDENTIALS in .env?")
        raise
