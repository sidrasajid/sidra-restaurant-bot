from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):

    await websocket.accept()

    print("Client connected!")

    try:
        while True:

            message = await websocket.receive_text()

            print(f"Guest: {message}")

            response = f"Welcome to The Gourmet Table! You said: {message}"

            await websocket.send_text(response)

    except WebSocketDisconnect:

        print("Client disconnected!")