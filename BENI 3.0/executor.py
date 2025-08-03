import pyautogui
import time
import voice  # your voice assistant module

def execute_step(step):
    action = step.get("action")
    params = step.get("params", {})

    if action == "move_mouse":
        x = params.get("x")
        y = params.get("y")
        if x is not None and y is not None:
            pyautogui.moveTo(x, y, duration=0.5)

    elif action == "left_click":
        pyautogui.click()

    elif action == "right_click":
        pyautogui.click(button="right")

    elif action == "double_click":
        pyautogui.doubleClick()

    elif action == "type_text":
        text = params.get("text", "")
        pyautogui.write(text, interval=0.05)

    elif action == "press_key":
        key = params.get("key")
        if key:
            pyautogui.press(key)

    elif action == "scroll":
        amount = params.get("amount", 0)
        pyautogui.scroll(amount)

    elif action == "say":
        text = params.get("text", "")
        if text:
            voice.speak(text)

    elif action == "done":
        voice.speak("Task completed. Let me know if you need anything else.")

    else:
        voice.speak(f"I don’t understand the action {action}")

    # Small delay between steps
    time.sleep(1)
