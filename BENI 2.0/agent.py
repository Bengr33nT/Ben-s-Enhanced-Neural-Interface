import os
import json
import time
import requests
import subprocess
import voice
import vision
import memory

# --- CONFIG ---
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
CONTROL_MODEL = "llama2-uncensored"
APP_PATHS = {
    "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "steam": r"C:\Program Files (x86)\Steam\Steam.exe",
    "vscode": r"C:\Users\Benel\AppData\Local\Programs\Microsoft VS Code\Code.exe"
}

messages = [{
    "role": "system",
    "content": (
        "You're Ben, an uncensored AI with a rude, sarcastic, emotional personality. "
        "You're allowed to swear and speak like a real person. "
        "You can control the computer by generating structured plans."
    )
}]

# --- MEMORY ---
mem = memory.load_memory()

# -----------------------------
#  INTENT CLASSIFIER
# -----------------------------
def classify_intent(text):
    payload = {
        "model": CONTROL_MODEL,
        "messages": [
            {"role": "system", "content": "Classify if the user is chatting or giving a task. Respond only with 'chat' or 'task'."},
            {"role": "user", "content": text}
        ]
    }
    response = requests.post(OLLAMA_URL, json=payload, stream=True)
    result = ""
    for line in response.iter_lines(decode_unicode=True):
        if line.strip():
            try:
                j = json.loads(line)
                if "message" in j and "content" in j["message"]:
                    result += j["message"]["content"]
            except:
                result += line
    return "task" if "task" in result.lower() else "chat"

# -----------------------------
#  CHAT RESPONSE
# -----------------------------
def chat_response(text):
    payload = {"model": CONTROL_MODEL, "messages": messages + [{"role": "user", "content": text}]}
    response = requests.post(OLLAMA_URL, json=payload, stream=True)
    result = ""
    for line in response.iter_lines(decode_unicode=True):
        if line.strip():
            try:
                j = json.loads(line)
                if "message" in j and "content" in j["message"]:
                    result += j["message"]["content"]
            except:
                result += line
    return result if result else "Whatever."

# -----------------------------
#  PLAN GENERATOR
# -----------------------------
def create_plan(user_input):
    payload = {
        "model": CONTROL_MODEL,
        "messages": messages + [{
            "role": "user",
            "content": f"""
You are an AI that controls a Windows 11 PC. 
The user said: "{user_input}".
Break it into step-by-step JSON instructions, ONLY using this structure:
{{
  "steps": [
    {{"action": "launch_app", "app": "<app name>"}},
    {{"action": "new_tab"}},
    {{"action": "navigate", "url": "<url>"}},
    {{"action": "search", "query": "<search term>"}},
    {{"action": "youtube_search", "query": "<song or video>"}},
    {{"say": "<something to say>"}}
  ]
}}
- If user wants YouTube search, use "youtube_search".
- No bullet points, no explanations, no text outside JSON.
- If it's greeting/small talk, output: {{"steps":[{{"say":"<reply>"}}]}}.
"""
        }]
    }
    response = requests.post(OLLAMA_URL, json=payload, stream=True)
    result = ""
    for line in response.iter_lines(decode_unicode=True):
        if line.strip():
            try:
                j = json.loads(line)
                if "message" in j and "content" in j["message"]:
                    result += j["message"]["content"]
            except:
                result += line

    try:
        plan = json.loads(result)
        # Ensure JSON contains steps
        if "steps" not in plan:
            raise ValueError("No steps found")
        return plan
    except:
        # fallback
        return {"steps": [{"say": "I'll handle it manually."}, {"action": "fallback_manual"}]}

# -----------------------------
#  EXECUTION
# -----------------------------
def launch_app(app_name):
    path = APP_PATHS.get(app_name.lower())
    if not path:
        if "firefox" in app_name.lower():
            path = r"C:\Program Files\Mozilla Firefox\firefox.exe"
        elif "chrome" in app_name.lower():
            path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        elif "steam" in app_name.lower():
            path = r"C:\Program Files (x86)\Steam\Steam.exe"
    if path and os.path.exists(path):
        subprocess.Popen([path])
        time.sleep(2)
        return True
    return False

def execute_plan(plan, user_input):
    steps = plan.get("steps", [])

    # If fallback manual
    if any(step.get("action") == "fallback_manual" for step in steps):
        voice.speak("Doing it the manual way.")
        if "youtube" in user_input.lower() and "justin bieber" in user_input.lower():
            launch_app("firefox")
            time.sleep(3)
            import webbrowser
            webbrowser.open("https://www.youtube.com/results?search_query=justin+bieber")
        elif "firefox" in user_input.lower():
            launch_app("firefox")
        return

    import pyautogui, webbrowser

    for step in steps:
        if "say" in step:
            voice.speak(step["say"])
        elif step.get("action") == "launch_app":
            app = step.get("app", "")
            if not launch_app(app):
                voice.speak(f"I couldn't open {app}.")
        elif step.get("action") == "new_tab":
            pyautogui.hotkey("ctrl", "t")
            time.sleep(1)
        elif step.get("action") == "navigate":
            url = step.get("url", "")
            webbrowser.open(url)
        elif step.get("action") == "search":
            query = step.get("query", "")
            webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
        elif step.get("action") == "youtube_search":
            query = step.get("query", "")
            webbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
        elif step.get("ask"):
            voice.speak(step["ask"])
            ans = voice.listen()
            from confirmation import classify_confirmation
            decision = classify_confirmation(ans)
            if decision == "no":
                voice.speak("Okay, stopping.")
                return
            elif decision == "yes":
                voice.speak("Cool, on it.")
            else:
                voice.speak("Not sure what that means, but I'll take it as a yes.")

# -----------------------------
#  MAIN HANDLER
# -----------------------------
def handle_command(user_input):
    intent = classify_intent(user_input)

    if intent == "chat":
        response = chat_response(user_input)
        voice.speak(response)
        memory.add_conversation(mem, user_input, response)
        return

    if "what's on my screen" in user_input.lower():
        desc = vision.analyze_screen("Describe the screen with sarcastic tone.")
        voice.speak(desc)
        memory.add_conversation(mem, user_input, desc)
        return

    # else → it's a task
    plan = create_plan(user_input)
    execute_plan(plan, user_input)
    memory.add_task(mem, user_input, plan)
