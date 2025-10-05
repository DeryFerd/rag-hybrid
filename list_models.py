# list_models.py
import os
from google import genai

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not set")

client = genai.Client(api_key=api_key)

print("Available models:")
for model in client.models.list():
    if "flash" in model.name or "pro" in model.name:
        print(f"- {model.name} → {model.description[:60]}...")