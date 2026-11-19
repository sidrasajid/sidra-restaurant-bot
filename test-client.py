import asyncio
import websockets

async def run_client():
    uri = "ws://127.0.0.1:8000/ws/chat"
    
    # Test queries specifically targeting general conversation and the check_table tool
    queries = [
        "Hi! Do you have gluten-free options on your menu?",
        "Can I check table availability for 4 guests on 2026-11-20?",
        "What about a large party of 10 guests on that same date?"
    ]
    
    async with websockets.connect(uri) as websocket:
        for idx, query in enumerate(queries, start=1):
            print(f"\n================ Turn {idx} ================")
            print(f"User: {query}")
            print("Bot : ", end="", flush=True)
            
            await websocket.send(query)
            
            while True:
                token = await websocket.recv()
                if token == "[DONE]":
                    break
                print(token, end="", flush=True)
            print()

if __name__ == "__main__":
    asyncio.run(run_client())