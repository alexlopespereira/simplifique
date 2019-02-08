# encoding=utf8

# Imports the Google Cloud client library
import math
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import os
import requests
import base64
import boto3
import json
import scipy.stats as st
from math import sqrt

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/alex/Downloads/dev/simplifique/teste-d4c28fba69d8.json"


def ci_lower_bound(pos, n, confidence=None, z=None):
    if n == 0:
        return 0
    if z is None:
        z = st.norm.ppf(1 - (1 - confidence) / 2)
    phat = 1.0 * pos / n
    return (phat + z * z / (2 * n) - z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)) / (1 + z * z / n)


def score(positive, negative):
    return (((positive + 1.9208) / (positive + negative) - 1.96 * sqrt(((positive * negative) / (positive + negative)) + 0.9604) / (positive + negative)) / (1 + 3.8416 / (positive + negative)));


def fiveStarRating(qtd_ratings):
    positive = qtd_ratings[2] * 0.25 + qtd_ratings[3] * 0.5 + qtd_ratings[4] * 0.75 + qtd_ratings[5]
    negative = qtd_ratings[1] + qtd_ratings[2] * 0.75 + qtd_ratings[3] * 0.5 + qtd_ratings[4] * 0.25
    return score(positive, negative)


def fiveStarRatingAverage(avg, total):

    positive = (avg * total - total) / 4
    negative = total - positive
    return score(positive, negative)


def google_sentment(text):
    client = language.LanguageServiceClient()
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT,
        language='pt')

    sentiment = client.analyze_sentiment(document=document).document_sentiment
    if sentiment.score > 0:
        label = 'POSITIVE'
    elif sentiment.score > 0:
        label = 'NEGATIVE'
    else:
        if sentiment.magnitude == 0:
            label = 'MIXED'
        else:
            label = 'NEUTRAL'

    return {"score":sentiment.score, "magnitude": sentiment.magnitude , 'label':label}


def gotitai_sentment(text):
    url = 'https:#api.gotit.ai/NLU/v1.2/Analyze'
    data = {"T":text,"S":"true","EM":"true"}
    data_json = json.dumps(data)
    userAndPass = base64.b64encode(b"239-ms83EYUL:Ahhgf+ArIml63A7nR7U1nsUeKcGXlAHkoFGIyOdwUfcc").decode("ascii")
    headers = {'Content-type': 'application/json', "Authorization": "Basic %s" %  userAndPass}
    response = requests.post(url, data=data_json, headers=headers)
    return response.json()['sentiment']


def amazon_sentment(text):
    comprehend = boto3.client(service_name='comprehend', region_name='us-west-2')
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

# text = """Emoção do começo ao fim! Um filme que retrata a história de um dos melhores cantores história. Difícil você não interagir junto."""
# result = gotitai_sentment(text)
# print result
#
# result = google_sentment(text)
# print result
#
# result = amazon_sentment(text)
# print(result)


# Examples
# print(fiveStarRating([0, 0, 0, 0, 1]))      # 0.80390178246001
# print(fiveStarRating([0, 0, 0, 100, 0]))       # 0.46188074417216
# print(fiveStarRating([0, 1, 2, 6, 0] ))       # 0.33136280289755
# print(fiveStarRating([10, 1, 2, 0, 2] ))       # 0.079648861762752
# print(fiveStarRatingAverage(4.8000001907349, 10))          # 0.65545605272928


