import os
import time
from dotenv import load_dotenv
from groq import Groq
from utils.logger import get_logger


logger = get_logger("LLM Interaction")

load_dotenv()

def generate_response(messages):
    """
    Generates a text response using Groq's LLaMA API.
    
    Args:
        messages (list): List of message dictionaries (role, content).
        
    Returns:
        str: The generated text response.
    """
    logger.info("Starting text generation with context history.")
    
    if not messages:
        logger.warning("Empty messages provided for text generation.")
        return "No content to generate."

    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        client = Groq(api_key=groq_api_key)
        
        logger.info(f"⏱️ Calling Groq API (multi-turn) with {len(messages)} messages...")
        api_start = time.time()
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            max_tokens=2048
        )
        api_time = time.time() - api_start
        logger.info(f"✅ Groq API call completed in {api_time:.2f} seconds")
        
        response = completion.choices[0].message.content
        logger.info("Text generation successful.")
        return response
    except Exception as e:
        error_msg = f"Error during text generation: {str(e)}"
        logger.error(error_msg)
        return error_msg
