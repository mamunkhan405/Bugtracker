import asyncio
import websockets
import json

async def test_websocket():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU0MjE4OTUxLCJpYXQiOjE3NTQyMTUzNTEsImp0aSI6IjAyMWQzZDcyNjlmMTQwNWVhMmYwMmFiYjE0ZDJhZGU2IiwidXNlcl9pZCI6MX0.HZcnFHxmkmXjpp3PV-1UUVBZkF_MWF7Hx-ufZ_-_TzM"
    uri = f"ws://127.0.0.1:8000/ws/project/1/?token={token}"

    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({"type": "ping"}))
        async for message in websocket:
            print(f"Received: {message}")
            break


if __name__ == "__main__":
    asyncio.run(test_websocket())