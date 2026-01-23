

# Persistent memory for chat history


import json
import os

from utils.logger import get_logger


logger = get_logger("MEMORY")


HISTORY_FILE = "chat_history.json"

def load_history():

    """Reads chat_history.json. Returns {} if missing or invalid."""

    if not os.path.exists(HISTORY_FILE):

        return {}
    try:

        with open(HISTORY_FILE, "r", encoding="utf-8") as f:

            data = json.load(f)

            return data if isinstance(data, dict) else {}

    except Exception as e:

        logger.error(f"Failed to load history: {e}")

        return {}


def save_history(history):

    """Writes the full session dictionary to chat_history.json."""
    try:

        with open(HISTORY_FILE, "w", encoding="utf-8") as f:

            json.dump(history, f, indent=2, ensure_ascii=False)

    except Exception as e:

        logger.error(f"Failed to save history: {e}")

def clear_history():
    """Wipes everything on app restart by overwriting with an empty dict."""
    try:
        save_history({})
        logger.info("Chat history cleared (file overwritten).")
    except Exception as e:
        logger.error(f"Failed to clear history: {e}")


def add_to_history(session_id, role, content):

    """Appends a message to a specific session's history."""

    history = load_history()
    if session_id not in history:

        history[session_id] = []
    

    history[session_id].append({"role": role, "content": content})

    save_history(history)


def get_messages_for_llm(session_id, max_messages=10):
    """

    Returns history for a specific session formatted for the LLM API.
    """
    history = load_history()

    session_history = history.get(session_id, [])
    

    # Trim to window

    trimmed = session_history[-max_messages:] if len(session_history) > max_messages else session_history
    

    # Prepend system prompt

    messages = [{"role": "system", "content": "You are a helpful voice assistant. IMPORTANT RULE: If you receive incomplete phrases, out of context words, or words in another language different from the one the user initially started with: Ask the user politely to repeat that. IF the user EXPLICITLY states that he wants to switch language, then you can switch language."}]

    messages.extend(trimmed)
    

    return messages

