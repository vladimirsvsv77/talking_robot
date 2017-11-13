from examples.Python import snowboydecoder, settings
from yandex_speech import TTS
import os


def say_vera(text):
    tts = TTS("jane", "mp3", settings.YANDEX_SPEECH_API)
    tts.generate(text)
    tts.save()
    os.system("mpg123 speech.mp3")

def detected_callback():
    say_vera('hello')


detector = snowboydecoder.HotwordDetector("hello_vera.pmdl", sensitivity=0.5, audio_gain=1)
detector.start(detected_callback)
