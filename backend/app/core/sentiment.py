from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# ensure VADER lexicon
nltk.download("vader_lexicon", quiet=True)

_vader = SentimentIntensityAnalyzer()

def analyze_sentiment(text: str):
    if not text:
        return {"compound": 0.0, "tone": "neutral"}
    scores = _vader.polarity_scores(text)
    compound = scores["compound"]
    if compound >= 0.05:
        tone = "positive"
    elif compound <= -0.05:
        tone = "negative"
    else:
        tone = "neutral"
    return {"compound": compound, "tone": tone, "raw": scores}
