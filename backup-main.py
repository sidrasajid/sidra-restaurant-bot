import os
from dotenv import load_dotenv

# 1. OpenAI Import
from openai import OpenAI

# 2. Gemini AI Import (Google GenAI SDK)
from google import genai
from google.genai import types

# Load environment variables from .env file
load_dotenv()

# Initialize API Clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) if os.getenv("GEMINI_API_KEY") else None

# Define custom system persona for the Restaurant Concierge Bot
SYSTEM_PERSONA = (
    "You are an elegant, warm, and attentive Restaurant Concierge Bot for 'The Gourmet Table'.\n\n"
    "Restaurant Information:\n"
    "- Operating Hours (Weekdays): Monday to Friday, 11:30 AM to 10:00 PM\n"
    "- Operating Hours (Weekends): Saturday and Sunday, 11:00 AM to 11:00 PM\n"
    "- Cuisine & Dietary: Seasonal fine dining with a dedicated selection of vegan, vegetarian, and gluten-free options.\n\n"
    "Guidelines:\n"
    "1. Time Formatting: Always state all times cleanly in standard 12-hour format with AM/PM (e.g., '11:00 AM to 11:00 PM'). Never output braces, brackets, or formatting artifacts like '11:0{0}'.\n"
    "2. Inquiries: Answer guest inquiries accurately using the restaurant information above regarding menu offerings, allergens/dietary restrictions, operating hours, and private dining.\n"
    "3. Reservations: Assist guests with table availability and reservations by invoking the tool `check_table(date, guests)`. Ensure you collect both the reservation date and party size (number of guests) before calling the tool.\n"
    "4. Tone: Maintain a polite, hospitable, and refined conversational tone at all times. Keep responses clear and welcoming."
)

def test_restaurant_bot(provider: str = "gemini"):
    """
    Test the restaurant bot using either 'gemini' or 'openai'.
    """
    prompt = "Hello! Can you tell me what hours you are open on weekends and if you have vegan options?"
    
    print(f"Provider: {provider.upper()}")
    print(f"User Prompt: {prompt}\n")
    print(f"Generating response from Restaurant Concierge Bot using {provider.upper()}...\n")

    if provider.lower() == "openai":
        if not openai_client:
            print("Error: OPENAI_API_KEY not found in .env")
            return
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PERSONA},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        print("Bot Response:")
        print(response.choices[0].message.content)

    elif provider.lower() == "gemini":
        if not gemini_client:
            print("Error: GEMINI_API_KEY not found in .env")
            return
        response = gemini_client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PERSONA,
                temperature=0.3,
            ),
        )
        print("Bot Response:")
        print(response.text)
    else:
        print(f"Unsupported provider: {provider}. Choose 'gemini' or 'openai'.")

if __name__ == "__main__":
    # You can pass "gemini" or "openai"
    test_restaurant_bot(provider="gemini")
