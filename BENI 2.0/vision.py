import base64
import io
import json
import random
import time
import threading
import requests
from PIL import ImageGrab

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
VISION_MODEL = "llava"

def capture_screen():
    img = ImageGrab.grab()
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

def analyze_screen(prompt="Describe what you see."):
    image_bytes = capture_screen()
    b64_image = base64.b64encode(image_bytes).decode()

    payload = {
        "model": VISION_MODEL,
        "prompt": prompt,
        "images": [b64_image]
    }
    response = requests.post(OLLAMA_URL, json=payload, stream=True)

    result = ""
    for line in response.iter_lines(decode_unicode=True):
        if line.strip():
            try:
                j = json.loads(line)
                if "response" in j:
                    result += j["response"]
            except:
                result += line
    return result.strip()

# Random commentary thread
COMMENTARY = True
def random_commentary(callback):
    while COMMENTARY:
        time.sleep(random.randint(120, 300))  # every 2–5 min
        desc = analyze_screen("Summarize what is happening.")
        comment = f"So... {desc.lower()}. Should I help you with that?"
        callback(comment)
