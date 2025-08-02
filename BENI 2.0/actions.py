import os
import shutil
import subprocess
import pyautogui
import time

# Known apps dictionary (add paths for your system)
APP_PATHS = {
    "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "vs code": r"C:\Users\<YOUR_USERNAME>\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "steam": r"C:\Program Files (x86)\Steam\Steam.exe"
}

def launch_app(app_name):
    path = APP_PATHS.get(app_name.lower())
    if path and os.path.exists(path):
        subprocess.Popen([path])
        time.sleep(3)
        return True
    return False

def create_folder(path):
    os.makedirs(path, exist_ok=True)
    return True

def delete_path(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
        return True
    elif os.path.isfile(path):
        os.remove(path)
        return True
    return False

def rename_path(old, new):
    if os.path.exists(old):
        os.rename(old, new)
        return True
    return False

def open_folder(path):
    if os.path.exists(path):
        subprocess.Popen(["explorer", path])
        return True
    return False

def click(coords):
    pyautogui.moveTo(coords[0], coords[1])
    pyautogui.click()

def type_text(text):
    pyautogui.typewrite(text, interval=0.05)

def press_keys(keys):
    pyautogui.hotkey(*keys)
