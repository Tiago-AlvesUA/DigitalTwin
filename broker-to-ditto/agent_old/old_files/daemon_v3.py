# Description: This daemon will be running in cloud/edge to bridge the communication between the remote MQTT broker and the Ditto platform;
import paho.mqtt.client as mqtt
import json
import requests
from pygeotile.tile import Tile
import threading
import tiles

class bcolors:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    RED = '\033[93m'
    ENDC = '\033[0m'


BROKER_HOST = "es-broker.av.it.pt"
BROKER_PORT = 8090
MQTT_INITIAL_TOPIC = "its_center/inqueue/json/20/#" # TODO: Usage of geographical tiling here
MQTT_USERNAME = "it2s"
MQTT_PASSWORD = "it2sit2s"

DITTO_BASE_URL = "http://localhost:8080/api/2/things"
DITTO_THING_ID = "org.acme:my-device-2" # TODO: This can be dynamic (getting the device name), from the toml file
DITTO_USERNAME = 'ditto'
DITTO_PASSWORD = 'ditto'

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport='websockets')
current_tiled_topic = "placeholder"

def log_warning(message):
    print(bcolors.RED +message +bcolors.ENDC)

def update_ditto(payload):
    url = f"{DITTO_BASE_URL}/{DITTO_THING_ID}/features/C-ITS-Messages"
    # Set up headers and basic authentication
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    
    # Send HTTP PUT request to update the twin in Ditto
    response = requests.put(url, headers=headers, auth=(DITTO_USERNAME, DITTO_PASSWORD), json=payload)
    # if response.status_code in (201, 204):
    #     print("Ditto twin updated successfully.")
    # else:
    #     print(f"Failed to update Ditto twin. Status code: {response.status_code}")
    #     print("Response:", response.text)

def manage_current_tile(message):
    global current_tiled_topic

    topic = message.topic.split("/")
    quadtree_map = '/'.join(topic[5:])

    new_tiled_topic = f"its_center/inqueue/json/+/+/{quadtree_map}"
    if (new_tiled_topic == current_tiled_topic):
        return

    log_warning(f"Switching tiled subscription to new quadtree topic: {new_tiled_topic}")
    mqtt_client.unsubscribe(current_tiled_topic)
    mqtt_client.subscribe(new_tiled_topic)

    current_tiled_topic = new_tiled_topic


def send_to_ditto(message):
    payload_json = json.loads(message)

    ditto_payload = {
        "properties": payload_json
    }

    update_ditto(ditto_payload)

def on_message_cb(client, userdata, message):
    print("Received message on topic '" + message.topic)

    if ("its_center/inqueue/json/20/" in message.topic):
        manage_current_tile(message)

    send_to_ditto(message.payload)

def on_connect_cb(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print("failed to connect")

    print("Subscribing to topic: " + MQTT_INITIAL_TOPIC)
    mqtt_client.subscribe(MQTT_INITIAL_TOPIC)

def setup_initial_mqtt():
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_client.on_message = on_message_cb
    mqtt_client.on_connect = on_connect_cb
    mqtt_client.connect(BROKER_HOST, BROKER_PORT)

    return mqtt_client


def subscribe_to_get_vehicle_area():
    """ Subscribes to the own vehicle messages to get the current location. """
    client = setup_initial_mqtt()
    client.loop_forever()


def run_daemon():
    initial_thread = threading.Thread(target=subscribe_to_get_vehicle_area)
    initial_thread.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Broker-to-ditto daemon interrupted. Shutting down...")
        mqtt_client.disconnect()

if __name__ == "__main__":
    run_daemon()