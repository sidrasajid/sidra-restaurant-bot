
import os

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from google import genai
from google.genai import types


# --------------------------------------------------
# 1. LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")


# --------------------------------------------------
# 2. CONNECT TO GEMINI
# --------------------------------------------------

client = genai.Client(api_key=api_key)


# --------------------------------------------------
# 3. CREATE FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="The Gourmet Table - Restaurant Concierge Bot"
)


# --------------------------------------------------
# 4. RESTAURANT BOT PERSONALITY
# --------------------------------------------------

SYSTEM_PERSONA = """
You are an elegant, warm, and attentive Restaurant Concierge Bot
for 'The Gourmet Table'.

Restaurant Information:

- Operating Hours (Weekdays):
  Monday to Friday, 11:30 AM to 10:00 PM.

- Operating Hours (Weekends):
  Saturday and Sunday, 11:00 AM to 11:00 PM.

- Cuisine and Dietary:
  Seasonal fine dining with a dedicated selection
  of vegan, vegetarian, and gluten-free options.

Guidelines:

1. Always use standard 12-hour time format with AM/PM.

2. Answer guest inquiries accurately using the restaurant
   information provided.

3. Assist guests with menu, allergens, dietary restrictions,
   operating hours, and private dining inquiries.

4. For reservations, collect both the reservation date
   and number of guests before proceeding.

5. Maintain a polite, hospitable, and refined tone.
"""


# --------------------------------------------------
# 5. WEBSOCKET CHAT ENDPOINT
# --------------------------------------------------

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):

    # Accept WebSocket connection
    await websocket.accept()

    print("Guest connected!")

    # Conversation history for this connection
    messages = []

    try:

        while True:

            # Receive message from guest
            user_message = await websocket.receive_text()

            print(f"Guest: {user_message}")

            # Save guest message in conversation history
            messages.append({
                "role": "user",
                "parts": [
                    {"text": user_message}
                ]
            })

            # Store complete Gemini response
            bot_response = ""

            # Generate streaming response from Gemini
            response = client.models.generate_content_stream(
                model="gemini-3.5-flash-lite",
                contents=messages,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PERSONA,
                    temperature=0.3,
                ),
            )

            # Send response chunks to guest
            for chunk in response:

                if chunk.text:

                    # Add chunk to complete response
                    bot_response += chunk.text

                    # Send chunk immediately
                    await websocket.send_text(chunk.text)

            # Save Gemini response in conversation history
            messages.append({
                "role": "model",
                "parts": [
                    {"text": bot_response}
                ]
            })

            print(f"Bot: {bot_response}")

            # Tell client that response is complete
            await websocket.send_text("[DONE]")

    except WebSocketDisconnect:

        print("Guest disconnected!")

    except Exception as error:

        print(f"Error: {error}")

        try:
            await websocket.send_text(
                "Sorry, something went wrong. Please try again."
            )

            await websocket.send_text("[DONE]")

        except Exception:
            pass

#this is main file