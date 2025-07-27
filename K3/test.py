from modules.assistant_core import FridayAssistant

assistant = FridayAssistant()

print("Testing voice input...")
text = assistant.listen_to_voice()
print(f"You said: {text}")

print("\nTesting text-to-speech...")
assistant.speak("This is a test of the voice system")