# Description: This daemon will be running in cloud/edge to bridge the communication between the remote MQTT broker and the Ditto platform;
import paho.mqtt.client as mqtt
import json
import requests
from pygeotile.tile import Tile

BROKER_HOST = "es-broker.av.it.pt"
BROKER_PORT = 8090
MQTT_TOPIC = "its_center/inqueue/json/20" # TODO: Usage of geographical tiling here
MQTT_USERNAME = "it2s"
MQTT_PASSWORD = "it2sit2s"

DITTO_BASE_URL = "http://localhost:8080/api/2/things"
DITTO_THING_ID = "org.acme:my-device-2" # TODO: This can be dynamic (getting the device name), from the toml file
DITTO_USERNAME = 'ditto'
DITTO_PASSWORD = 'ditto'

mqtt_client = None

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


def on_message(client, userdata, message):
    payload_json = json.loads(message.payload)

    print("\n\nReceived message '" + str(payload_json) + "' on topic '" + message.topic + "'\n\n")
    ditto_payload = {
        "properties": payload_json
    }

    update_ditto(ditto_payload)

def get_vehicle_coordinates():
    url = f"{DITTO_BASE_URL}/{DITTO_THING_ID}/features/localTwin"

    response = requests.get(url, auth=(DITTO_USERNAME, DITTO_PASSWORD))

    if response.status_code == 200:
        feature_properties = response.json()
    else:
        print(f"Failed to get Ditto twin. Status code: {response.status_code}")
        print("Response:", response.text)
    
    latitude = feature_properties["properties"]["referencePosition"]["properties"]["latitude"]/10**7
    longitude = feature_properties["properties"]["referencePosition"]["properties"]["longitude"]/10**7

    return latitude, longitude

def setup_mqtt_topic_quadtree():
    """ Creates a TMS tile using the vehicle's current location and converts it to the Microsoft QuadTree format. """
    latitude, longitude = get_vehicle_coordinates()
    tile = Tile.for_latitude_longitude(latitude, longitude, 14) # Zoom level 14
    quadtree = tile.quad_tree
    return quadtree

def setup_mqtt():
    global mqtt_client

    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,transport='websockets')
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_client.on_message = on_message
    mqtt_client.connect(BROKER_HOST, BROKER_PORT)

    # Determine quadtree mapping for the vehicle's current location and append it to the MQTT topic
    quadtree_map = setup_mqtt_topic_quadtree()
    full_topic = f"{MQTT_TOPIC}/{quadtree_map}"
    print("Subscribing to topic: " + full_topic)
    mqtt_client.subscribe(full_topic)

    return mqtt_client

def run_daemon():
    """Main function to start the MQTT client and keep the daemon running."""

    client = setup_mqtt()
    client.loop_start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Broker-to-ditto daemon interrupted. Shutting down...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    run_daemon()