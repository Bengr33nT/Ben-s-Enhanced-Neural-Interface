import json
import requests
import vision
import actions
import voice
import memory  # <-- new

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
CONTROL_MODEL = "llama2-uncensored"

# Load memory at startup
mem = memory.load_memory()

messages = [{
    "role": "system",
    "content": (
        "You're Ben, an uncensored AI with a rude, sarcastic, emotional personality. "
        "You're allowed to swear, curse, and speak like a real person. "
        "You remember past conversations and tasks from memory."
        "Speak with short sentences."
    )
}]
# Add previous conversations to context
for convo in mem["conversations"][-5:]:  # last 5 for context
    messages.append({"role": "user", "content": convo["user"]})
    messages.append({"role": "assistant", "content": convo["assistant"]})

def handle_command(user_input):
    # Provide memory context summary
    mem_summary = f"Previous tasks: {len(mem['tasks'])}. Recent conversation: {len(mem['conversations'])}"
    full_instruction = f"{user_input}\nMemory context: {mem_summary}"

    screen_analysis = vision.analyze_screen(user_input)

    try:
        data = json.loads(screen_analysis)
    except json.JSONDecodeError:
        # fallback: treat as chat
        reply = chat_response(user_input)
        voice.speak(reply)
        memory.add_conversation(mem, user_input, reply)
        return

    if data.get("type") == "task":
        actions.execute(data.get("actions", []))
        voice.speak("Done. Happy now?")
        memory.add_task(mem, user_input, data.get("actions", []))
        memory.add_conversation(mem, user_input, "Done. Happy now?")
    else:
        reply = data.get("response", chat_response(user_input))
        voice.speak(reply)
        memory.add_conversation(mem, user_input, reply)

def chat_response(user_input=None):
    if user_input:
        messages.append({"role": "user", "content": user_input})
    payload = {"model": CONTROL_MODEL, "messages": messages}
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
    if not result:
        result = "Whatever."
    messages.append({"role": "assistant", "content": result})
    return result
