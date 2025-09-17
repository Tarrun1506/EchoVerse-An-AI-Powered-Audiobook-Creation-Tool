# services/granite_service.py
import os, requests

GRANITE_URL = os.getenv("GRANITE_URL")
GRANITE_KEY = os.getenv("GRANITE_API_KEY")

def rewrite_text(text: str, tone: str) -> str:
    prompt = f"Rewrite the following text in a {tone} tone, preserving meaning:\n\n{text}"
    headers = {"Authorization": f"Bearer {GRANITE_KEY}"}
    response = requests.post(
        GRANITE_URL + "/v1/generate",
        json={"prompt": prompt, "max_tokens": len(text.split()) * 2},
        headers=headers
    )
    response.raise_for_status()
    return response.json()["choices"][0]["text"].strip()
