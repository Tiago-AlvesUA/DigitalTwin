# Description: This daemon will be running in cloud/edge to bridge the communication between the remote MQTT broker and the Ditto platform;
import paho.mqtt.client as mqtt
import json
import requests
from pygeotile.tile import Tile
import threading
import tiles
import time
import math

class bcolors:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    RED = '\033[93m'
    ENDC = '\033[0m'

    @classmethod
    def log_warning_red(cls, message):
        print(cls.RED +message +cls.ENDC)
    @classmethod
    def log_warning_blue(cls,message):
        print(cls.CYAN +message +cls.ENDC)

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
current_original_topic = "placeholder"
current_subscribed_topics = set()
local_map = []


def construct_json(local_map):
    neighbors_json = {
        "properties": {}
    }

    for obj in local_map:
        obj_id, obj_lat, obj_lon = obj
        neighbors_json["properties"][obj_id] = {
            "latitude": obj_lat,
            "longitude": obj_lon
        }

    # TODO: This is causing the slowdown of the system becuase the HTTP requests block the main thread
    update_ditto(neighbors_json)

def update_ditto(neighbors):
    url = f"{DITTO_BASE_URL}/{DITTO_THING_ID}/features/C-ITS-Messages"
    # Set up headers and basic authentication
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    
    # Send HTTP PUT request to update the twin in Ditto; TODO: Verify status code of response if needed
    response = requests.put(url, headers=headers, auth=(DITTO_USERNAME, DITTO_PASSWORD), json=neighbors)
    # if response.status_code in (201, 204):
    #     print("Ditto twin updated successfully.")
    # else:
    #     print(f"Failed to update Ditto twin. Status code: {response.status_code}")
    #     print("Response:", response.text)
    
# TODO
def ditto_sender():
    while (1):
        construct_json(local_map)
        local_map.clear()
        time.sleep(0.1) 

def cam_to_local_map(payload):
    payload = json.loads(payload)
    obj_id = payload["cam"]["camParameters"]["basicContainer"]["stationType"]
    obj_lat = payload["cam"]["camParameters"]["basicContainer"]["referencePosition"]["latitude"]
    obj_lon = payload["cam"]["camParameters"]["basicContainer"]["referencePosition"]["longitude"]
    local_map.append((obj_id, obj_lat, obj_lon))


def cpm_to_local_map(payload):
    payload = json.loads(payload)

    station_position = [
        payload["cpm"]["cpmParameters"]["managementContainer"]["referencePosition"]["latitude"] / 10e6,
        payload["cpm"]["cpmParameters"]["managementContainer"]["referencePosition"]["longitude"] / 10e6
    ]

    perceived_objects = payload["cpm"]["cpmParameters"].get("perceivedObjectContainer")
    if perceived_objects:
        for obj in perceived_objects:
            # Extract object data
            obj_id = obj["objectID"]
            obj_lat = station_position[0] + (obj["yDistance"]["value"] / 6371000 / 100) * (180 / math.pi) 
            obj_lon = station_position[1] + ((obj["xDistance"]["value"] / 6371000 / 100) * (180 / math.pi)) / math.cos(((station_position[0] + (obj["yDistance"]["value"] / 6371000 / 100) * (180 / math.pi)) * math.pi / 180))
            local_map.append((obj_id, obj_lat, obj_lon))


def manage_current_tile(message):
    # TODO: Testing and verification
    global current_original_topic, current_subscribed_topics

    topic = message.topic.split("/")
    original_topic_tile = '/'.join(topic[5:])
    original_topic_path = f"its_center/inqueue/json/+/+/{original_topic_tile}"
   
    # If vehicle did not change tile, don't need to modify subscriptions
    if (original_topic_path == current_original_topic):
        return

    bcolors.log_warning_blue(f"Switching original subscription to new quadtree topic: {original_topic_path}")

    it2s_tiles = tiles.It2s_Tiles()
    # Get the adjacent tiles (in all directions) NOTE: The original tile is also included, by calculation of Hold direction
    adjacent_tiles = set(it2s_tiles.it2s_get_all_adjacent_tiles(original_topic_tile))

    new_subscribed_topics = set()

    for tile in adjacent_tiles:
        tile_topic = f"its_center/inqueue/json/+/+/{tile}"
        new_subscribed_topics.add(tile_topic)
    
    topics_to_unsubscribe = current_subscribed_topics - new_subscribed_topics
    topics_to_subscribe = new_subscribed_topics - current_subscribed_topics
    
    for topic in topics_to_unsubscribe:
        #bcolors.log_warning_red(f"Unsubscribing from topic: {topic}")
        mqtt_client.unsubscribe(topic)

    for topic in topics_to_subscribe:
        #bcolors.log_warning_red(f"Subscribing to new topic: {topic}")
        mqtt_client.subscribe(topic)

    current_original_topic = original_topic_path
    current_subscribed_topics = new_subscribed_topics
    for topic in current_subscribed_topics:
        bcolors.log_warning_red(f"Subscribed to topic: {topic}")


def on_message_cb(client, userdata, message):
    #print("Received message on topic '" + message.topic)
    station_id = message.topic.split("/")[3]
    
    if (station_id == "20"):
        #print(bcolors.CYAN + "Received message on topic '" + message.topic + bcolors.ENDC)
        manage_current_tile(message)

    # TODO
    elif (station_id != 20):
        if ("CAM" in message.topic):
            cam_to_local_map(message.payload)
        elif ("CPM" in message.topic):
            cpm_to_local_map(message.payload)

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


def start_agent_threads():
    initial_thread = threading.Thread(target=subscribe_to_get_vehicle_area, daemon=True)
    initial_thread.start()

    ditto_thread = threading.Thread(target=ditto_sender, daemon=True)
    ditto_thread.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Broker-to-ditto daemon interrupted. Shutting down...")
        mqtt_client.disconnect()

if __name__ == "__main__":
    start_agent_threads()