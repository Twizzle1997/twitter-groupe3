#coding:utf-8

import tweepy
import json
import requests
from pprint import pprint
import smart_tweet_keys as stk
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from pymongo import MongoClient


keys = stk.Settings()
auth = tweepy.OAuthHandler(keys.CONSUMER_KEY, keys.CONSUMER_SECRET)
auth.set_access_token(keys.ACCESS_TOKEN, keys.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

endpoint = keys.AZURE_ENDPOINT
api_version = '?api-version=2020-06-30'
headers = {'Content-Type': 'application/json', 'api-key': keys.AZURE_KEY}

client = MongoClient("mongodb+srv://simplon:pMTPbkx4SEILUfam@cluster0.nqjp5.mongodb.net/business?retryWrites=true&w=majority")
db = client.smart_tweet_maxime
collection_xbox_tweet = db["xbox_tweet"]


def authenticate_client():
    ta_credential = AzureKeyCredential(keys.AZURE_KEY)
    text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=ta_credential)
    return text_analytics_client        


client = authenticate_client()

dico_tweet = []

for tweet in tweepy.Cursor(api.search,  q = "#XboxSeriesS", lang = "fr").items(150):
    if tweet.retweeted == False:
        temp = {}
        temp['ID'] = tweet.id
        temp['Texte'] = tweet.text
        temp['Date'] = tweet.created_at.strftime("%Y-%d-%m")
        temp['Auteur'] = tweet.user.screen_name
        response = client.analyze_sentiment(documents = [tweet.text])[0]
        temp['Sentiment'] = []
        temp['Sentiment Score'] = temp['Sentiment'].response.sentiment
        temp['Confidence Scores'] = []
        temp['Score Positif'] = temp['Confidence Scores'].response.confidence_scores.positive
        temp['Score Neutre'] = temp['Confidence Scores'].response.confidence_scores.neutral
        temp['Score Negatif'] = temp['Confidence Scores'].response.confidence_scores.negative
        dico_tweet.append(temp)

collection_xbox_tweet.insert_many(dico_tweet)
client.close()

with open('xbox_tweet.json', 'w') as json_file:
    json.dump(dico_tweet, json_file)