import os
import requests

# IBM Watson configuration
IBM_URL = os.getenv("IBM_URL")
IBM_KEY = os.getenv("IBM_API_KEY")

def synthesize_speech(text: str, voice: str) -> bytes:
    # IBM Watson TTS
    response = requests.post(
        f"{IBM_URL}/v1/synthesize",
        auth=("apikey", IBM_KEY),
        headers={
            "Content-Type": "application/json",
            "Accept": "audio/mp3"
        },
        json={"text": text, "voice": f"en-US_{voice}V3Voice"}
    )
    response.raise_for_status()
    return response.content