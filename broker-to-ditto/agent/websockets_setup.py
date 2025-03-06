import asyncio
#import signal
import websockets
from websockets.exceptions import ConnectionClosed
from websockets.asyncio.server import serve

CLIENTS = set()

async def handler(websocket):
    CLIENTS.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        CLIENTS.remove(websocket)

async def broadcast(message):
    for websocket in CLIENTS.copy():
        try:
            await websocket.send(message)
        except ConnectionClosed:
            pass

async def broadcast_messages():
    while True:
        await asyncio.sleep(1)
        message = "1 sec diff"
        await broadcast(message)

# async def echo(websocket):
#     #clients.add(websocket)

#     await websocket.send("Hello from server!")

#     count = 0
#     try:
#         while True:
#             await asyncio.sleep(5)
#             count +=1
#             await websocket.send("Periodic message from server")
#     except websockets.exceptions.ConnectionClosed:
#             print("Client disconnected. Stopping periodic messages.")

#     async for message in websocket:
#         await websocket.send(f"Server says: {message}")

async def main():
    async with serve(handler, "localhost", 8765) as server:
        await broadcast_messages()
        #await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())