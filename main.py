import voice
import agent

while True:
    user_input = voice.listen()
    if not user_input:
        continue
    print(f"You: {user_input}")

    if user_input.lower() in ["exit", "quit", "bye"]:
        voice.speak("Alright, I'm out.")
        break

    agent.handle_command(user_input)
