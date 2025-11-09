import threading
from workers.mqtt import setup_initial_mqtt
from workers.ditto_listener import start_ditto_ws_listener
from workers.ditto_sender import start_sender_ws_listener

stop_event = threading.Event()

def subscribe_to_get_vehicle_area():
    """ Subscribes to the own vehicle messages to get the current location. """
    setup_initial_mqtt()

def start_agent_thread():
    mqtt_thread = threading.Thread(target=subscribe_to_get_vehicle_area, daemon=True)
    mqtt_thread.start()

    ditto_ws_thread = threading.Thread(target=start_ditto_ws_listener, daemon=True)
    ditto_ws_thread.start()

    sender_ws_thread = threading.Thread(target=start_sender_ws_listener, daemon=True)
    sender_ws_thread.start()

    mqtt_thread.join()
    ditto_ws_thread.join()
    sender_ws_thread.join()
    

if __name__ == "__main__":
    start_agent_thread()