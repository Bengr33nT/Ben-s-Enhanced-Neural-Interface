import json
import requests
import vision
import actions
import voice
import memory
import threading

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
CONTROL_MODEL = "llama2-uncensored"

mem = memory.load_memory()

messages = [{
    "role": "system",
    "content": (
        "You're Ben, an uncensored, sarcastic, rude AI assistant. "
        "You can control the user's PC, plan steps before doing tasks, "
        "occasionally comment on what they're doing, and ask for clarification if needed."
    )
}]

# Commentary background thread
def commentary_callback(text):
    voice.speak(text)
threading.Thread(target=vision.random_commentary, args=(commentary_callback,), daemon=True).start()

def handle_command(user_input):
    if "what's on my screen" in user_input.lower():
        desc = vision.analyze_screen("Describe the screen with sarcastic tone.")
        voice.speak(desc)
        memory.add_conversation(mem, user_input, desc)
        return

    # Ask model to create plan
    plan = create_plan(user_input)
    execute_plan(plan, user_input)

def create_plan(user_input):
    context = f"User said: {user_input}\nPrevious tasks: {len(mem['tasks'])}"
    payload = {
        "model": CONTROL_MODEL,
        "messages": messages + [{"role": "user", "content": f"Create a step-by-step JSON plan for: {context}"}]
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
        return json.loads(result)
    except:
        return {"steps": [{"say": "I have no idea what you want."}]}

def execute_plan(plan, user_input):
    for step in plan.get("steps", []):
        if "say" in step:
            voice.speak(step["say"])
        elif "ask" in step:
            voice.speak(step["ask"])
            ans = voice.listen().lower()
            if "no" in ans:
                voice.speak("Okay, stopping.")
                return
        elif step.get("action") == "launch_app":
            actions.launch_app(step["app"])
        elif step.get("action") == "new_tab":
            actions.press_keys(["ctrl", "t"])
        elif step.get("action") == "navigate":
            actions.type_text(step["url"] + "\n")
        elif step.get("action") == "search":
            actions.type_text(step["query"] + "\n")
        elif step.get("action") == "click_first_result":
            actions.press_keys(["tab"])
            actions.press_keys(["enter"])
        elif step.get("action") == "create_folder":
            actions.create_folder(step["path"])
        elif step.get("action") == "delete_path":
            actions.delete_path(step["path"])
        elif step.get("action") == "rename_path":
            actions.rename_path(step["old"], step["new"])
        elif step.get("action") == "open_folder":
            actions.open_folder(step["path"])
    voice.speak("All done.")
    memory.add_task(mem, user_input, plan)
    memory.add_conversation(mem, user_input, "Task completed.")
