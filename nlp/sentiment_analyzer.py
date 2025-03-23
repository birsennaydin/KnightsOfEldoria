# nlp/sentiment_analyzer.py
from textblob import TextBlob

def analyze_sentiment(text: str) -> float:
    """
    Analyze the sentiment polarity of a text using TextBlob.
    Returns a float between -1.0 (very negative) to 1.0 (very positive).
    """
    blob = TextBlob(text)
    return blob.sentiment.polarity
