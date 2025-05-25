# Description: This daemon will be running in cloud/edge to bridge the communication between the remote MQTT broker and the Ditto platform;
import threading
import asyncio
from workers.mqtt import setup_initial_mqtt
from workers.webserver import start_websocket_server, send_to_visualizer
from workers.shared_memory import messages

def subscribe_to_get_vehicle_area():
    """ Subscribes to the own vehicle messages to get the current location. """
    setup_initial_mqtt()


# TODO: Se possível utilizar para ambos mqtt e websocket threads ou asyncio
def start_agent_thread():
    # Thread number 2 to start the MQTT client
    initial_thread = threading.Thread(target=subscribe_to_get_vehicle_area, daemon=True)
    initial_thread.start()

    # Async tasks - start WS server and message processor concurrently (running in the main thread)
    async def websocket_task():
        """Starts the WebSocket server"""
        await start_websocket_server()

    async def message_processor():
        while True:
            msg = await asyncio.to_thread(messages.get)  # Get item from queue
            await send_to_visualizer(msg)

    async def main():
        task1 = asyncio.create_task(websocket_task())
        task2 = asyncio.create_task(message_processor())
        await asyncio.gather(task1, task2)

    # Start the event loop properly
    asyncio.run(main())


if __name__ == "__main__":
    # Main thread
    start_agent_thread()