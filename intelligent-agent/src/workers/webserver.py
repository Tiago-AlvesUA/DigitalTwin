import asyncio
from config import WS_HOST, WS_PORT
from websockets.exceptions import ConnectionClosed
from websockets.asyncio.server import serve
# from workers.shared_memory import get_message_from_queue

FRONTEND_CLIENTS = set()


async def start_websocket_server():
    print("Starting websockets server")
    async with serve(handler, WS_HOST, WS_PORT) as server:
        #await asyncio.gather(server.serve_forever(), send_to_visualizer())
        await server.serve_forever()

async def handler(websocket):
    FRONTEND_CLIENTS.add(websocket)
    print(FRONTEND_CLIENTS)
    try:
        await websocket.wait_closed()
    finally:
        FRONTEND_CLIENTS.remove(websocket)


async def send_to_visualizer(message):
    if FRONTEND_CLIENTS:
        for websocket in FRONTEND_CLIENTS.copy():
            try:
                await websocket.send(message)
            except ConnectionClosed:
                pass
