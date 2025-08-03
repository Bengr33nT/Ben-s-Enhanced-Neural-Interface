import voice
import vision
import executor
import time

def main():
    voice.speak("Ben is awake. What the hell do you want?")

    while True:
        user_instruction = voice.listen().strip()
        if not user_instruction:
            continue

        if user_instruction.lower() in ["exit", "quit", "stop"]:
            voice.speak("Finally, peace. Bye.")
            break

        voice.speak(f"Got it: {user_instruction}. I’m on it.")

        done = False
        while not done:
            screenshot = vision.capture_screenshot()
            step = vision.get_next_step(user_instruction, screenshot)
            if step.get("action") == "done":
                executor.execute_step(step)
                done = True
            else:
                executor.execute_step(step)

if __name__ == "__main__":
    main()
