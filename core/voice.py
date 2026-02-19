# termux_version/core/voice.py
import os
import threading

# v29000: ETERNITY VOICE SYSTEM
# Gives the system a voice using Termux API.

def speak(text):
    """
    Uses termux-tts-speak to announce messages.
    Run in thread to avoid blocking.
    """
    def _speak():
        try:
            # Escape quotes
            safe_text = text.replace("'", "").replace('"', "")
            os.system(f"termux-tts-speak '{safe_text}' > /dev/null 2>&1")
        except: pass

    t = threading.Thread(target=_speak)
    t.daemon = True
    t.start()

def announce_startup():
    speak("System Online. Welcome back, Commander.")

def announce_attack(target):
    speak(f"Engaging target {target}")
