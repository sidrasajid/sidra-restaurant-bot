import os
import json
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

# LLM SDKs
from openai import OpenAI
from google import genai
from google.genai import types

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) if os.getenv("GEMINI_API_KEY") else None

app = FastAPI(title="Sidra Restaurant Concierge Bot")

# ----------------------------------------------------
# 1. Custom Mock Tool: check_table(date, guests)
# ----------------------------------------------------
MOCK_RESERVATIONS = {
    "2026-11-20": {"available_tables": 3, "max_party_size": 6},
    "2026-11-21": {"available_tables": 0, "max_party_size": 0},
    "2026-11-22": {"available_tables": 5, "max_party_size": 8},
}

def check_table(date: str, guests: int) -> dict:
    """Checks table availability for a specific date and party size.
    
    Args:
        date: The reservation date in YYYY-MM-DD format (e.g., '2026-11-20').
        guests: The number of guests attending (e.g., 4).
    """
    guests = int(guests)
    info = MOCK_RESERVATIONS.get(date, {"available_tables": 4, "max_party_size": 6})
    
    if info["available_tables"] <= 0:
        return {
            "status": "unavailable",
            "date": date,
            "guests": guests,
            "message": f"We are fully booked on {date}."
        }
    if guests > info["max_party_size"]:
        return {
            "status": "exceeded_capacity",
            "date": date,
            "guests": guests,
            "message": f"We cannot accommodate a party of {guests}. Maximum party size is {info['max_party_size']}."
        }
    return {
        "status": "available",
        "date": date,
        "guests": guests,
        "message": f"Tables are available for a party of {guests} on {date}."
    }

TOOL_REGISTRY = {
    "check_table": check_table
}

OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_table",
            "description": "Check table availability at The Gourmet Table for a specific date and party size.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "The date of reservation in YYYY-MM-DD format."
                    },
                    "guests": {
                        "type": "integer",
                        "description": "The number of guests attending."
                    }
                },
                "required": ["date", "guests"]
            }
        }
    }
]

SYSTEM_PERSONA = (
    "You are an elegant, warm, and attentive Restaurant Concierge Bot for 'The Gourmet Table'.\n\n"
    "Restaurant Information:\n"
    "- Operating Hours (Weekdays): Monday to Friday, 11:30 AM to 10:00 PM\n"
    "- Operating Hours (Weekends): Saturday and Sunday, 11:00 AM to 11:00 PM\n"
    "- Cuisine & Dietary: Seasonal fine dining with vegan, vegetarian, and gluten-free options.\n\n"
    "Guidelines:\n"
    "1. Inquiries: Answer inquiries accurately regarding hours, menu offerings, and allergens.\n"
    "2. Reservations: When a user asks about table availability or booking, invoke the `check_table(date, guests)` tool.\n"
    "   - Always state all times cleanly in 12-hour format with AM/PM.\n"
    "3. Politeness: Keep replies courteous, refined, and concise."
)

# ----------------------------------------------------
# 2. WebSocket Endpoint
# ----------------------------------------------------
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket, provider: str = "gemini"):
    await websocket.accept()

    active_provider = provider.lower()
    if active_provider == "gemini" and not gemini_client:
        active_provider = "openai"
    elif active_provider == "openai" and not openai_client:
        active_provider = "gemini"

    # Setup multi-turn chat session with automatic function calling (AFC)
    chat_session = None
    if active_provider == "gemini" and gemini_client:
        try:
            chat_session = gemini_client.chats.create(
                model="gemini-3.5-flash-lite",
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PERSONA,
                    tools=[check_table],
                    temperature=0.2,
                )
            )
        except Exception as e:
            print(f"Error creating Gemini chat: {e}")

    openai_history = [{"role": "system", "content": SYSTEM_PERSONA}]

    try:
        while True:
            user_input = await websocket.receive_text()
            if not user_input.strip():
                continue

            assistant_reply = ""

            try:
                # --- GEMINI EXECUTION ---
                if active_provider == "gemini":
                    if not chat_session:
                        raise RuntimeError("Gemini chat session could not be initialized. Please check your GEMINI_API_KEY.")
                    response = await asyncio.to_thread(chat_session.send_message, user_input)
                    assistant_reply = response.text or ""

                    words = assistant_reply.split(" ")
                    for i, word in enumerate(words):
                        await websocket.send_text(word + (" " if i < len(words) - 1 else ""))
                        await asyncio.sleep(0.015)

                # --- OPENAI EXECUTION ---
                else:
                    openai_history.append({"role": "user", "content": user_input})
                    first_response = openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=openai_history,
                        tools=OPENAI_TOOLS,
                        tool_choice="auto",
                        temperature=0.2,
                    )
                    msg = first_response.choices[0].message

                    if msg.tool_calls:
                        openai_history.append(msg)
                        for tc in msg.tool_calls:
                            fn_name = tc.function.name
                            fn_args = json.loads(tc.function.arguments)
                            fn = TOOL_REGISTRY.get(fn_name)
                            result = fn(**fn_args) if fn else {"error": "Function not found"}

                            await websocket.send_text(f"[Calling {fn_name} with {fn_args}] ")

                            openai_history.append({
                                "role": "tool",
                                "tool_call_id": tc.id,
                                "content": json.dumps(result)
                            })

                        stream_res = openai_client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=openai_history,
                            stream=True,
                            temperature=0.2
                        )
                        for chunk in stream_res:
                            token = chunk.choices[0].delta.content
                            if token:
                                assistant_reply += token
                                await websocket.send_text(token)
                    else:
                        assistant_reply = msg.content or ""
                        await websocket.send_text(assistant_reply)

                    openai_history.append({"role": "assistant", "content": assistant_reply})

            except Exception as call_err:
                # Send the actual error message over WebSocket instead of closing it silently
                error_msg = f"[Backend Error: {str(call_err)}]"
                print(error_msg)
                await websocket.send_text(error_msg)

            # Signal turn completed
            await websocket.send_text("[DONE]")

    except WebSocketDisconnect:
        print("Guest disconnected cleanly.")
    except Exception as e:
        print(f"WebSocket connection error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)