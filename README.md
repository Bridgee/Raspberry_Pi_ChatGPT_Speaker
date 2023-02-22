# Raspberry_Pi_ChatGPT_Speaker

This code is a voice assistant based on the popular ChatGPT. It has been tested on Raspberry Pi 3b+ with a 2-mics Pi HAT, but it can be run on different platforms. You only need to change the PyAudio setup accordingly.

-----

## Basic

Following the structure from [nickbild](https://github.com/acheong08/ChatGPT-lite), the voice is first recorded using [PyAudio](https://pypi.org/project/PyAudio/). 

Then, using the [Google's Speech-to-Text API](https://cloud.google.com/speech-to-text/docs), the wav file is transcribed to text with selected language. Note that if you want mixed-language (e.g. En+Zh) transcription, [Whisper]((https://openai.com/blog/whisper/)) is a better option. 

Next step is to sent the text to ChatGPT. As there is no official API for it, a [reverse Engineered ChatGPT API](https://github.com/acheong08/ChatGPT)) is implemented, which requires personal authentication. 

Finally, the response from ChatGPT is convert to audio using [Google's Text-to-Speech API]((https://cloud.google.com/text-to-speech/docs/basics))

-----

## Hardware

* 1 x Raspberry Pi (any version)
* 1 x [reSpeaker 2-Mics Pi HAT]((https://github.com/respeaker/seeed-voicecard))

##  Setup

* Install driver of the Mic Hat following the [documentation](https://github.com/respeaker/seeed-voicecard).

* Check the hardware id using `aplay -l`  and `arecord -l`.
* Register, enable, and download your google API key and name it as google_key.json.
* Copy your session token of ChatGPT from [here](https://chat.openai.com/api/auth/session) to chatGPT_session_token.json.
* Change S2T and T2S language in the code, now it is zh.
* Change PyAudio setup such as  `input_device_index and `channels` based on your audio device

## How to use

After running ask_and_response.py, the script is waiting for GPIO button to activate the assistant.