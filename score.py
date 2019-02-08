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



def score(positive, negative):
    return (((positive + 1.9208) / (positive + negative) - 1.96 * sqrt(((positive * negative) / (positive + negative)) + 0.9604) / (positive + negative)) / (1 + 3.8416 / (positive + negative)));


def fiveStarRating(qtd_ratings):
    positive = qtd_ratings[2] * 0.25 + qtd_ratings[3] * 0.5 + qtd_ratings[4] * 0.75 + qtd_ratings[5]
    negative = qtd_ratings[1] + qtd_ratings[2] * 0.75 + qtd_ratings[3] * 0.5 + qtd_ratings[4] * 0.25
    return score(positive, negative)


# Examples
print(fiveStarRating({1:0, 2:0, 3:0, 4:0, 5:1}))
print(fiveStarRating({1:0, 2:0, 3:0, 4:100, 5:0}))
print(fiveStarRating({1:0, 2:1, 3:2, 4:6, 5:0} ))       # 0.33136280289755
print(fiveStarRating({1:10, 2:1, 3:2, 4:0, 5:2} ))       # 0.079648861762752

