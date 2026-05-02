from google import genai
import os

# Configure with your API key
gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)

# Use the new model name (Gemini 3 Flash Live)
response = client.models.generate_content(
    model="models/gemma-3-12b-it",
    contents="Generate a simple English paragraph for TOEIC Speaking Test Part 1. That should include 40-50 words and be about a daily life topic."
)
print(response.text)