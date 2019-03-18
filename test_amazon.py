import boto3
import json

AWS_SERVER_PUBLIC_KEY="Sua chave publica"
AWS_SERVER_SECRET_KEY="Sua chave secreta"
def amazon_sentment(text):
    comprehend = boto3.client(service_name='comprehend', region_name='us-west-2', aws_access_key_id = AWS_SERVER_PUBLIC_KEY,
    aws_secret_access_key = AWS_SERVER_SECRET_KEY)
    rjson = comprehend.detect_sentiment(Text=text, LanguageCode='pt')
    rjson['SentimentScore']['label'] = rjson['Sentiment']
    positive = rjson['SentimentScore']['Positive']
    negative = rjson['SentimentScore']['Negative']
    neutral = rjson['SentimentScore']['Neutral']
    if positive >= negative:
        if positive >= neutral:
            score = positive
        else:
            score = neutral
    else:
        if negative >= neutral:
            score = -negative
        else:
            score = neutral

    rjson['SentimentScore']['score'] = score
    return rjson['SentimentScore']

text = """Emoção do começo ao fim! Um filme que retrata a história de um dos melhores cantores história. Difícil você não interagir junto."""

result = amazon_sentment(text)
print(result)
