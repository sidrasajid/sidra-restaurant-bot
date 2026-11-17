
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load API key from .env file
load_dotenv()

# Check API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env")
    exit()

# Connect to Gemini
client = genai.Client(api_key=api_key)

# Restaurant Bot instructions
SYSTEM_PERSONA = """
You are a friendly Restaurant Concierge Bot
for The Gourmet Table.

Restaurant Information:
- Monday to Friday: 11:30 AM to 10:00 PM
- Saturday and Sunday: 11:00 AM to 11:00 PM
- Vegan and gluten-free options are available.

Answer guests politely and clearly.
"""

# Ask Gemini a question
prompt = "Hello! What are your weekend opening hours?"

print("Guest:", prompt)
print("\nRestaurant Bot: ", end="", flush=True)

# Generate a streaming response
response = client.models.generate_content_stream(
    model="gemini-3.5-flash-lite",
    contents=prompt,
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_PERSONA,
        temperature=0.3,
    ),
)

# Display response chunk by chunk
for chunk in response:
    if chunk.text:
        print(chunk.text, end="", flush=True)

print("\n\nResponse completed!")
