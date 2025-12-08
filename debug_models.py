from dotenv import load_dotenv
import os
from google import genai

load_dotenv("Youtube_Agent/.env")
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found in Youtube_Agent/.env")
else:
    client = genai.Client(api_key=api_key)
    print("Listing available models...")
    for m in client.models.list(config={"page_size": 100}):
        # m is a Model object, checking if it supports generation
        if "generateContent" in (m.supported_actions or []):
             print(f"- {m.name}")
