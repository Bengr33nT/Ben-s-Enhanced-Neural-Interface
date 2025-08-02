import os
import uuid
import time
import json
import vosk
import pyaudio
import pygame
from gtts import gTTS

# --- Initialization ---
model = vosk.Model("vosk-model")  # Your Vosk model folder
recognizer = vosk.KaldiRecognizer(model, 16000)
pygame.mixer.init()

def speak(text):
    filename = f"response_{uuid.uuid4()}.mp3"
    try:
        tts = gTTS(text=text, lang='en')
        tts.save(filename)

        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        time.sleep(0.1)
        pygame.mixer.music.unload()
    finally:
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except PermissionError:
                print(f"⚠️ Could not delete: {filename}")

def listen():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                    input=True, frames_per_buffer=8000)
    stream.start_stream()

    print("🎙️ Listening...")
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            text = json.loads(result).get("text", "")
            if text:
                stream.stop_stream()
                stream.close()
                p.terminate()
                return text
