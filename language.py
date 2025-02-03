from langdetect import detect
from log import Log

logger = Log("language")

def language(text):
    logger.trace(f"Starting lang detection in {text}")
    try:
        result = detect(text)
        logger.trace(f"Lang detection: {result}")
    except Exception as e:
        result = 'pt'
        logger.warn(f"Error processing language for {text}! {e.args}, {e.with_traceback()}")
    
    return result