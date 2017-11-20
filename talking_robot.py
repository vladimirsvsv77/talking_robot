
# -*- coding: utf-8 -*-
import requests

from examples.Python import snowboydecoder, settings
from yandex_speech import TTS
import os

from examples.Python.talking_robot.google_asr import start_google_asr

RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/vladimir/client_secret_749995213658-skse23o912beobhvddd94khcku8669l9.apps.googleusercontent.com.json"
bing_endpoint = 'https://api.cognitive.microsoft.com/bing/v5.0/search?mkt=en-us&responseFilter=Webpages&q='


def say_vera(text):
    tts = TTS("jane", "mp3", settings.YANDEX_SPEECH_API)
    tts.generate(text)
    tts.save()
    os.system("mpg123 speech.mp3")


def get_answer_bing(question):
    req = requests.get(bing_endpoint+question, headers={'Ocp-Apim-Subscription-Key': settings.bing_api_key})
    return  req.json()['webPages']['value'][0]['snippet']

def detected_callback():
    asr = start_google_asr()
    print(asr)
    detector = snowboydecoder.HotwordDetector("hello_vera.pmdl", sensitivity=0.5, audio_gain=1)
    detector.start(detected_callback)


detector = snowboydecoder.HotwordDetector("hello_vera.pmdl", sensitivity=0.5, audio_gain=1)
detector.start(detected_callback)


# def get_bloomberg_titles():
#     from bs4 import BeautifulSoup
#
#     news_url = 'https://www.bloomberg.com/view/topics/russia'
#
#     req = requests.get(news_url)
#
#     soup = BeautifulSoup(req.text, "html.parser")
#     titles = soup.find_all('h1', {'class': 'title_3Ob7U'})
#
#     titles_text = []
#
#     for i in titles:
#         titles_text.append(i.text)
#
#     return titles_text[:3]
#
#
# news = requests.post('https://ai.robotvera.com/stafory/getbloombergtitles/')
#
# print(news.text)
# news_speak = 'Top news: '+news[0].replace('\n', '')+'. Also in Russia: '+news[1].replace('\n','')
#
#
# json_responce = {"outputSpeech": {
#     "type": "SSML",
#     "ssml": "<speak>"+news_speak+"</speak>"
# }}
#
# print(json_responce)