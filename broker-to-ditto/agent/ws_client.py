import asyncio
from websockets.asyncio.client import connect


async def hello():
    async with connect("ws://localhost:8765") as websocket:
        #await websocket.send("Hello world!")
        while True:
            message = await websocket.recv()
            print(message)
            #await websocket.close()



if __name__ == "__main__":
    asyncio.run(hello())