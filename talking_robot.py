# -*- coding: utf-8 -*-
import requests

from examples.Python import snowboydecoder, settings
from yandex_speech import TTS
import os
import re
import sys

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import pyaudio
from six.moves import queue


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


class MicrophoneStream(object):
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)


def listen_print_loop(responses):
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript

        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + '\r')
            sys.stdout.flush()

            num_chars_printed = len(transcript)

        else:
            print(transcript + overwrite_chars)
            say_vera(get_answer_bing(transcript + overwrite_chars))
            detector.start(detected_callback)
            break


def start_google_asr():
    language_code = 'ru'  # a BCP-47 language tag

    client = speech.SpeechClient()
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)
    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        listen_print_loop(responses)


def detected_callback():
    start_google_asr()


detector = snowboydecoder.HotwordDetector("hello_vera.pmdl", sensitivity=0.5, audio_gain=1)
detector.start(detected_callback)