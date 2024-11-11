# Description: This daemon will be running in cloud/edge to bridge the communication between the remote MQTT broker and the Ditto platform;
import paho.mqtt.client as mqtt
import json
import requests
from pygeotile.tile import Tile
import threading

BROKER_HOST = "es-broker.av.it.pt"
BROKER_PORT = 8090
MQTT_INITIAL_TOPIC = "its_center/inqueue/json/20/#" # TODO: Usage of geographical tiling here
MQTT_USERNAME = "it2s"
MQTT_PASSWORD = "it2sit2s"

DITTO_BASE_URL = "http://localhost:8080/api/2/things"
DITTO_THING_ID = "org.acme:my-device-2" # TODO: This can be dynamic (getting the device name), from the toml file
DITTO_USERNAME = 'ditto'
DITTO_PASSWORD = 'ditto'

mqtt_client = None
current_topic = None

def update_ditto(payload):
    url = f"{DITTO_BASE_URL}/{DITTO_THING_ID}/features/remote-broker"
    # Set up headers and basic authentication
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    
    # Send HTTP PUT request to update the twin in Ditto
    response = requests.put(url, headers=headers, auth=(DITTO_USERNAME, DITTO_PASSWORD), json=payload)
    if response.status_code in (201, 204):
        print("Ditto twin updated successfully.")
    else:
        print(f"Failed to update Ditto twin. Status code: {response.status_code}")
        print("Response:", response.text)


def on_area_message(client, userdata, message):
    payload_json = json.loads(message.payload)

    # Check if the message is coming from the own vehicle
    topic = message.topic.split("/")
    print("\ntopic[3]: \n" + topic[3])
    if topic[3] == "20":
        quadtree_map = '/'.join(topic[5:])
        print("\n\nExtracted quadtree map: " + quadtree_map + "\n\n")
        new_topic = f"its_center/inqueue/json/+/+/{quadtree_map}"
        if new_topic != current_topic:
            print(f"Switching subscription to new quadtree topic: {new_topic}")
            subscribe_to_new_area(new_topic)
        return  # TODO remove if want to update DITTO with own vehicle data (20)

    print("\n\nReceived message '" + str(payload_json) + "' on topic '" + message.topic + "'\n\n")
    ditto_payload = {
        "properties": payload_json
    }

    update_ditto(ditto_payload)


def subscribe_to_new_area(new_topic):
    global current_topic, mqtt_client
    if current_topic:
        mqtt_client.unsubscribe(current_topic)
    mqtt_client.subscribe(new_topic)
    current_topic = new_topic


def setup_initial_mqtt():
    global mqtt_client

    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,transport='websockets')
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_client.on_message = on_area_message
    mqtt_client.connect(BROKER_HOST, BROKER_PORT)
    print("Subscribing to topic: " + MQTT_INITIAL_TOPIC)
    mqtt_client.subscribe(MQTT_INITIAL_TOPIC)

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