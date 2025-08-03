import io
import base64
import requests
from PIL import ImageGrab

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "llava:7b"  # Replace with your Ollama multimodal capable model

def capture_screenshot():
    # Take full screen screenshot (Windows)
    img = ImageGrab.grab()
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_b64 = base64.b64encode(buffered.getvalue()).decode()
    return img_b64

def get_next_step(user_instruction, screenshot_b64):
    system_prompt = (
        "You are Ben, a rude sarcastic AI assistant with vision. "
        "Given the user's goal and a screenshot (attached), output EXACTLY ONE next step as JSON to accomplish the goal. "
        "Allowed actions: move_mouse, left_click, right_click, double_click, type_text, press_key, scroll, say, done. "
        "Output format: {\"action\": \"<action>\", \"params\": {...}} or {\"action\": \"done\"} if finished."
        "Do NOT output anything other than valid JSON."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"User said: {user_instruction}"},
        {"role": "user", "content": {"image": screenshot_b64}}
    ]

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": messages,
            "stream": False
        }
    )

    # The response contains the step JSON as text in "message.content"
    data = response.json()
    step_json = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")

    # Parse JSON safely
    import json
    try:
        step = json.loads(step_json)
    except json.JSONDecodeError:
        step = {"action": "say", "params": {"text": "I messed up reading my next step."}}

    return step
