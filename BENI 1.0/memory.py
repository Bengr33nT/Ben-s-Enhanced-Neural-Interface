import json
import os

MEMORY_FILE = "memory.json"
MAX_CONVERSATIONS = 50
MAX_TASKS = 50

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except:
            return {"conversations": [], "tasks": []}
    return {"conversations": [], "tasks": []}

def save_memory(memory):
    # prune old data
    memory["conversations"] = memory["conversations"][-MAX_CONVERSATIONS:]
    memory["tasks"] = memory["tasks"][-MAX_TASKS:]
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def add_conversation(memory, user, assistant):
    memory["conversations"].append({"user": user, "assistant": assistant})
    save_memory(memory)

def add_task(memory, instruction, actions):
    memory["tasks"].append({"instruction": instruction, "actions": actions})
    save_memory(memory)
