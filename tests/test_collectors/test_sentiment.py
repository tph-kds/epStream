from processing.sentiment import analyze_sentiment

def test_sentiment_positive():
    text = "I love this product! It's absolutely wonderful."
    score, sentiment_label = analyze_sentiment(text)
    assert sentiment_label == "positive"
    assert score > 0

def test_sentiment_negative():
    text = "This is the worst experience I've ever had."
    score, sentiment_label = analyze_sentiment(text)
    assert sentiment_label == "negative"
    assert score < 0

    