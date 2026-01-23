import logging
import os

LOG_FILE = "voice_assistant.log"

# Configure logging with the specified format and handlers
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def get_logger(name):
    """
    Returns a logger with the specified name.
    """
    return logging.getLogger(name)
