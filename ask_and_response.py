#!/usr/bin/python

import pyaudio
import wave
from google.cloud import speech
from revChatGPT.V1 import Chatbot
from google.cloud import texttospeech
import RPi.GPIO as GPIO
import time
import os
import json

# config
BUTTON = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN)

client_s2t = speech.SpeechClient.from_service_account_file('google_key.json')
client_t2s = texttospeech.TextToSpeechClient.from_service_account_file('google_key.json')

s2t_config = speech.RecognitionConfig(
    sample_rate_hertz = 16000,
    enable_automatic_punctuation = True,
    language_code = 'zh',
    audio_channel_count = 2
)

voice = texttospeech.VoiceSelectionParams(
    language_code="zh", 
    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
)

audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16
)

with open('chatGPT_session_token.json', 'r') as f:
    chatGPT_config = json.load(f)

chatbot = Chatbot(
    config = chatGPT_config
)

RESPEAKER_RATE = 16000
RESPEAKER_CHANNELS = 2 
RESPEAKER_WIDTH = 2
# run getDeviceInfo.py to get index
RESPEAKER_INDEX = 2  # refer to input device id
CHUNK = 1024 * 2
RECORD_SECONDS = 5
RECORD_FILENAME = "output.wav"
RESPONSE_FILENAME = "result.wav"

os.system('clear')
btn_first_flg = True
while True:
    state = GPIO.input(BUTTON)
    if state:
        if btn_first_flg:
            print("Push button to activate")
            btn_first_flg = False
    else:
        btn_first_flg = True

        ##### Record #####
        p = pyaudio.PyAudio()
        stream = p.open(
                    rate=RESPEAKER_RATE,
                    format=p.get_format_from_width(RESPEAKER_WIDTH),
                    channels=RESPEAKER_CHANNELS,
                    input=True,
                    input_device_index=RESPEAKER_INDEX,)

        print("Recording {} seconds...".format(RECORD_SECONDS))

        frames = []
        for i in range(0, int(RESPEAKER_RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK, exception_on_overflow = False)
            frames.append(data)

        print("Done recording...")

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(RECORD_FILENAME, 'wb')
        wf.setnchannels(RESPEAKER_CHANNELS)
        wf.setsampwidth(p.get_sample_size(p.get_format_from_width(RESPEAKER_WIDTH)))
        wf.setframerate(RESPEAKER_RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        ##### Speech to Text #####
        with open(RECORD_FILENAME, 'rb') as f:
            wav_data = f.read()

        audio_file = speech.RecognitionAudio(content=wav_data) 

        print("Speech to text...")
        s2t_response = client_s2t.recognize(
            config = s2t_config,
            audio = audio_file
        )
        print("Done speech to text...")

        ##### ChatGPT #####
        for result in s2t_response.results:
            gpt_prompt = result.alternatives[0].transcript
            gpt_response = ''
            print(gpt_prompt)

        print("Asking ChatGPT...")
        for data in chatbot.ask(gpt_prompt):
            gpt_response = data["message"]

        print("Got ChatGPT response...")
        print(gpt_response)

        ##### Response to speech #####
        synthesis_input = texttospeech.SynthesisInput(text = gpt_response)
        t2s_response = client_t2s.synthesize_speech(
            input = synthesis_input, 
            voice = voice, 
            audio_config = audio_config
        )

        ##### Save speech #####
        print("Saving wav file...")
        with open(RESPONSE_FILENAME, "wb") as f:
            f.write(t2s_response.audio_content)
        print("Playing response...")
        os.system('aplay ' + RESPONSE_FILENAME)
        print("All done!")
