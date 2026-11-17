
import asyncio
import websockets


async def run_client():

    uri = "ws://localhost:8000/ws/chat"

    conversation = [
        "Hello! What kind of cuisine do you serve?",
        "Do you have vegan and gluten-free options?",
        "What are your operating hours on weekends?"
    ]

    async with websockets.connect(uri) as websocket:

        print("Connected to The Gourmet Table!")

        for turn_num, user_msg in enumerate(conversation, start=1):

            print(f"\n========== Turn {turn_num} ==========")

            print(f"Guest: {user_msg}")

            print("Bot: ", end="", flush=True)

            # Send guest message
            await websocket.send(user_msg)

            # Receive streamed response
            while True:

                token = await websocket.recv()

                if token == "[DONE]":
                    break

                print(token, end="", flush=True)

            print()


if __name__ == "__main__":
    asyncio.run(run_client())
