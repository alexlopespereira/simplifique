# encoding=utf8

# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import os
import json
import requests
import pprint
import base64

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/alex/Downloads/dev/simplifique/teste-d4c28fba69d8.json"

def google_sentment(text):
    # Instantiates a client
    client = language.LanguageServiceClient()

    # The text to analyze
    # text = u'Hello, world!'
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    # Detects the sentiment of the text
    sentiment = client.analyze_sentiment(document=document).document_sentiment

    return {"score":sentiment.score, "magnitude": sentiment.magnitude }


def gotitai_sentment(text):
    url = 'https://api.gotit.ai/NLU/v1.2/Analyze'
    data = {"T":text,"S":"true","E":"true"}
    data_json = json.dumps(data)
    userAndPass = base64.b64encode(b"239-ms83EYUL:Ahhgf+ArIml63A7nR7U1nsUeKcGXlAHkoFGIyOdwUfcc").decode("ascii")
    headers = {'Content-type': 'application/json', "Authorization": "Basic %s" %  userAndPass}
    response = requests.post(url, data=data_json, headers=headers)
    #pprint.pprint(response.json())
    return response.json()['sentiment']


# text = "Eu não gostei do hotel. A cama era ruim."
# result = gotitai_sentment(text)
# print result
#
# result = google_sentment(text)
# print result

import boto3
import json


comprehend = boto3.client(service_name='comprehend', region_name='us-west-2')

text = "It is raining today in Seattle"

print('Calling DetectSentiment')
print(json.dumps(comprehend.detect_sentiment(Text=text, LanguageCode='pt'), sort_keys=True, indent=4))
print('End of DetectSentiment\n')
