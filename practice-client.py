
import asyncio
import websockets

async def test_connection():
    uri = "ws://localhost:8000/ws/chat"

    async with websockets.connect(uri) as websocket:
        print("Connected to Restaurant Bot!")

        message = "Hello, how are you?"
        print("Guest:", message)

        await websocket.send(message)

        response = await websocket.recv()
        print("Bot:", response)

asyncio.run(test_connection())
