import pyautogui
import time

def execute(actions):
    for act in actions:
        a = act.get("action")
        if a == "move_mouse":
            x, y = act.get("x"), act.get("y")
            pyautogui.moveTo(x, y, duration=0.2)
        elif a == "click":
            pyautogui.click()
        elif a == "right_click":
            pyautogui.click(button="right")
        elif a == "type":
            text = act.get("text", "")
            pyautogui.typewrite(text, interval=0.05)
        elif a == "hotkey":
            keys = act.get("keys", [])
            pyautogui.hotkey(*keys)
        time.sleep(0.2)
