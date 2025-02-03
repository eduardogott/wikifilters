from langdetect import detect

def language(text):
    return detect(text)