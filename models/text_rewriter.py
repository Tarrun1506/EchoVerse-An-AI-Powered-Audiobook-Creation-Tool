from huggingface_hub import InferenceApi, HfApi
import os
import json
from dotenv import load_dotenv

load_dotenv()

class TextRewriter:
    def __init__(self):
        self.model_id = "ibm-granite/granite-3.1-8b-instruct"
        self.token = os.getenv("HUGGINGFACE_TOKEN")
        try:
            self.client = InferenceApi(repo_id=self.model_id, token=self.token)
            print(f"TextRewriter initialized with model: {self.model_id}")
        except Exception as e:
            print(f"Error initializing TextRewriter: {e}. Falling back to no rewriting.")
            self.client = None  # Fallback to no API client

    def rewrite_text(self, text: str, tone: str, max_length: int = 300) -> str:
        """
        Rewrite text with a specified tone
        
        Args:
            text: Input text to rewrite
            tone: Desired tone (e.g., neutral, suspenseful, inspiring)
            max_length: Maximum length of the rewritten text
        
        Returns:
            Rewritten text or original text if rewriting fails
        """
        if not text or len(text) > max_length:
            text = text[:max_length] if len(text) > max_length else text
        
        if self.client is None:
            print("No rewriting client available. Returning original text.")
            return text
        
        tone_prompts = {
            "neutral": (
                "Rewrite the following text in a clear, neutral, and professional tone while preserving the original meaning:\n\n"
                f"{text}\n\nRewritten text:"
            ),
            "suspenseful": (
                "Rewrite the following text in a suspenseful, mysterious tone that builds tension while keeping the original meaning:\n\n"
                f"{text}\n\nRewritten text:"
            ),
            "inspiring": (
                "Rewrite the following text in an inspiring, uplifting, and motivational tone while preserving the original meaning:\n\n"
                f"{text}\n\nRewritten text:"
            )
        }
        prompt = tone_prompts.get(tone, tone_prompts["neutral"])

        if len(prompt) > 2000:
            truncated_text = text[:1500] + "..."
            prompt = tone_prompts[tone].replace(text, truncated_text)

        try:
            response = self.client(
                {
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": max_length,
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "do_sample": True
                    }
                },
                raw_response=True
            )

            if response.headers.get('content-type', '').startswith("application/json"):
                data = json.loads(response.content)
                if isinstance(data, list) and data and "generated_text" in data[0]:
                    generated = data[0]["generated_text"]
                else:
                    generated = ""
            else:
                generated = response.content.decode("utf-8")

            if "Rewritten text:" in generated:
                rewritten = generated.split("Rewritten text:")[-1].strip()
            else:
                rewritten = generated[len(prompt):].strip()

            return self._clean_output(rewritten) or text
        except Exception as e:
            print(f"Error rewriting text: {e}. Returning original text.")
            return text

    def _clean_output(self, text: str) -> str:
        text = text.strip()
        sentences = text.split('.')
        if len(sentences) > 1 and len(sentences[-1].strip()) < 10:
            text = '.'.join(sentences[:-1]) + '.'
        unwanted_phrases = [
            "Here is the rewritten text:",
            "Rewritten version:",
            "Here's the text rewritten:",
            "The rewritten text is:"
        ]
        for phrase in unwanted_phrases:
            text = text.replace(phrase, "").strip()
        return text