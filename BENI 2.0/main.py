import voice
import agent

while True:
    user_input = voice.listen()
    if user_input.lower() in ["quit", "exit", "bye"]:
        voice.speak("Later loser.")
        break
    agent.handle_command(user_input)
