import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing from .env")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Say hello in one sentence.",
)

print(response.text)

usage = response.usage_metadata
print(f"Input tokens: {usage.prompt_token_count}")
print(f"Output tokens: {usage.candidates_token_count}")
