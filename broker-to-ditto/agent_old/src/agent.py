# Description: This daemon will be running in cloud/edge to bridge the communication between the remote MQTT broker and the Ditto platform;
import threading
import asyncio
from mqtt_handler import setup_initial_mqtt
from websockets_server import start_websocket_server, send_to_visualizer
import global_vars

def subscribe_to_get_vehicle_area():
    """ Subscribes to the own vehicle messages to get the current location. """
    setup_initial_mqtt()
    global_vars.mqtt_client.loop_forever()


def start_agent_thread():
    # Thread number 2 to start the MQTT client
    initial_thread = threading.Thread(target=subscribe_to_get_vehicle_area, daemon=True)
    initial_thread.start()

    # Async tasks - start WS server and message processor concurrently (running in the main thread)
    async def websocket_task():
        """Starts the WebSocket server"""
        await start_websocket_server()

    async def message_processor():
        """Processes messages and sends them to the WebSocket clients"""
        while True:
            msg = await asyncio.to_thread(global_vars.message_queue.get)  # Get item from queue
            await send_to_visualizer(msg)

    async def main():
        """Runs both the WebSocket server and the message processor concurrently"""
        await asyncio.gather(websocket_task(), message_processor())

    # Start the event loop properly
    asyncio.run(main())



if __name__ == "__main__":
    # Main thread
    start_agent_thread()