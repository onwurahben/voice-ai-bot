import re 

def clean_text_for_tts(text):
    """
    Removes Markdown and special characters that sound unnatural when spoken.
    """
    # 1. Remove bold/italic asterisks (e.g., **bold**, *italic*)
    text = text.replace("*", "")
    
    # 2. Remove hashtag headers (e.g., # Header)
    text = re.sub(r'#+\s+', '', text)
    
    # 3. Remove backticks (code blocks)
    text = text.replace("`", "")
    
    # 4. Clean up multiple spaces or newlines left behind
   # text = re.sub(r'\s+', ' ', text).strip()
    
    return text