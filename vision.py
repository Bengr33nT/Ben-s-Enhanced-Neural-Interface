import mss
import base64
import requests
import io
from PIL import Image

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
VISION_MODEL = "llava:7b"  # Replace with your Ollama multimodal model

def capture_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

def analyze_screen(user_instruction):
    image_data = capture_screen()
    b64_image = base64.b64encode(image_data).decode()

    prompt = f"""
    You are Ben, a rude, sarcastic AI that controls a computer. 
    Instruction: "{user_instruction}"
    Current screen image is provided.
    If this is a command to operate the computer, output JSON:
    {{
      "type": "task",
      "actions": [{{"action": "...", "x": 0, "y": 0, "text": "..."}}]
    }}
    If it's just chat, output JSON:
    {{
      "type": "chat",
      "response": "your rude reply"
    }}
    """

    response = requests.post(OLLAMA_URL, json={
    "model": VISION_MODEL,
    "prompt": prompt,
    "images": [b64_image]
    }, stream=True)

    output = ""
    for line in response.iter_lines(decode_unicode=True):
        if line.strip():
            try:
                j = json.loads(line)
                if "response" in j:
                    output += j["response"]
            except:
                output += line
    return output.strip()


