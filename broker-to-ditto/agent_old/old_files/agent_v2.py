# Description: This daemon will be running in cloud/edge to bridge the communication between the remote MQTT broker and the Ditto platform;
import paho.mqtt.client as mqtt
import json
import requests
import threading
import tiles
import time
import math
import asyncio
import queue
from websockets.exceptions import ConnectionClosed
from websockets.asyncio.server import serve

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
MQTT_INITIAL_TOPIC = "its_center/inqueue/json/22/#" # TODO: Usage of geographical tiling here
MQTT_USERNAME = "it2s"
MQTT_PASSWORD = "it2sit2s"

DITTO_BASE_URL = "http://localhost:8080/api/2/things"
DITTO_THING_ID = "org.acme:my-device-1" # TODO: This can be dynamic (getting the device name), from the toml file
DITTO_USERNAME = 'ditto'
DITTO_PASSWORD = 'ditto'

FRONTEND_CLIENTS = set()
WS_HOST = "localhost"
WS_PORT = 8765

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport='websockets')
current_original_topic = "placeholder"
current_subscribed_topics = set()
last_local_perception_update = 0
last_local_awareness_update = 0

message_queue = queue.Queue()

############ WEBSOCKETS ############

async def send_to_visualizer(message):
    if FRONTEND_CLIENTS:
        for websocket in FRONTEND_CLIENTS.copy():
            try:
                await websocket.send(message)
            except ConnectionClosed:
                pass

async def start_websocket_server():
    print("Starting websockets server")
    async with serve(handler, WS_HOST, WS_PORT) as server:
        await server.serve_forever()

async def handler(websocket):
    FRONTEND_CLIENTS.add(websocket)
    print(FRONTEND_CLIENTS)
    try:
        await websocket.wait_closed()
    finally:
        FRONTEND_CLIENTS.remove(websocket)

####################################

def obtain_dynamics(payload):

    payload = json.loads(payload)

    device_id = payload["header"]["stationId"]

    cam = payload["cam"]["camParameters"]
    timestamp = payload["cam"]["generationDeltaTime"]

    ### Basic container ###
    sta_type = cam["basicContainer"]["stationType"]
    ref_pos = cam["basicContainer"]["referencePosition"]
    
    ### HF container ###
    high_freq_container = cam["highFrequencyContainer"]["basicVehicleContainerHighFrequency"]

    heading = high_freq_container["heading"]
    speed = high_freq_container["speed"]
    drive_direction = high_freq_container["driveDirection"]
    long_accel = high_freq_container["longitudinalAcceleration"]
    curv = high_freq_container["curvature"]
    curv_calc_mode = high_freq_container["curvatureCalculationMode"]
    yaw_rate = high_freq_container["yawRate"]
    
    ### LF container ###
    if "lowFrequencyContainer" in cam:
        low_freq_container = cam["lowFrequencyContainer"]["basicVehicleContainerLowFrequency"]

        vehicle_role = low_freq_container["vehicleRole"]
        ext_lights = low_freq_container["exteriorLights"]
        path_hist = low_freq_container["pathHistory"]

        dynamics = {
            "properties": {
                "generationDeltaTime": timestamp,
                "basicContainer": {
                    "stationType": sta_type,
                    "referencePosition": ref_pos
                },
                "highFrequencyContainer": {
                    "heading": heading,
                    "speed": speed,
                    "driveDirection": drive_direction,
                    "longitudinalAcceleration": long_accel,
                    "curvature": curv,
                    "curvatureCalculationMode": curv_calc_mode,
                    "yawRate": yaw_rate
                },
                "lowFrequencyContainer": {
                    "vehicleRole": vehicle_role,
                    "exteriorLights": ext_lights,
                    "pathHistory": path_hist
                }
            }
        }
    # If there is no LF container, just don't include it in the dynamics
    else:
        dynamics = {
            "properties": {
                "generationDeltaTime": timestamp,
                "basicContainer": {
                    "stationType": sta_type,
                    "referencePosition": ref_pos
                },
                "highFrequencyContainer": {
                    "heading": heading,
                    "speed": speed,
                    "driveDirection": drive_direction,
                    "longitudinalAcceleration": long_accel,
                    "curvature": curv,
                    "curvatureCalculationMode": curv_calc_mode,
                    "yawRate": yaw_rate
                }
            }
        }

    return device_id, dynamics
    #update_ditto_dynamics(dynamics)

def create_awareness_json(timestamp, local_awareness):
    objects_json = {
        "properties": {
            "generationDeltaTime": timestamp
        }
    }

    for obj in local_awareness:
        id, type, lat, lon = obj
        objects_json["properties"][id] = {
            "stationType": type,
            "latitude": lat,
            "longitude": lon
        }

    return objects_json


def create_perception_json(timestamp, local_perception):
    objects_json = {
        "properties": {
            "generationDeltaTime": timestamp
        }
    }

    for obj in local_perception:
        id, lat, lon, speed, class_name, class_type = obj
        objects_json["properties"][id] = {
            "latitude": lat,
            "longitude": lon,
            "speed": speed,
            "classification": {
                "class": {
                    class_name: {
                        "type": class_type
                    }
                }
            }
        }

    return objects_json

        
def cpm_to_local_perception(payload):
    # TODO: Distinguish CPM versions here?

    payload = json.loads(payload)

    # New local map to be updated
    local_perception = []

    timestamp = payload["cpm"]["generationDeltaTime"]

    station_position = [
        payload["cpm"]["cpmParameters"]["managementContainer"]["referencePosition"]["latitude"] / 1e7,
        payload["cpm"]["cpmParameters"]["managementContainer"]["referencePosition"]["longitude"] / 1e7
    ]

    perceived_objects = payload["cpm"]["cpmParameters"].get("perceivedObjectContainer")

    if perceived_objects:
        # Calculate the position of the perceived objects and add them to local map
        for obj in perceived_objects:
            obj_id = obj["objectID"]
            obj_lat = station_position[0] + (obj["yDistance"]["value"] / 6371000 / 100) * (180 / math.pi) 
            obj_lon = station_position[1] + ((obj["xDistance"]["value"] / 6371000 / 100) * (180 / math.pi)) / math.cos(((station_position[0] + (obj["yDistance"]["value"] / 6371000 / 100) * (180 / math.pi)) * math.pi / 180))
            
            obj_speed_kmh = round(float(math.sqrt(math.pow(obj["xSpeed"]["value"],2) + math.pow(obj["ySpeed"]["value"],2))) * 0.036, 1)
            
            if obj["classification"] and obj["classification"][0] and obj["classification"][0]["class"]:
                obj_class_name = list(obj["classification"][0]["class"].keys())[0]
                obj_class_type = obj["classification"][0]["class"][obj_class_name]["type"]

            local_perception.append((obj_id, obj_lat, obj_lon, obj_speed_kmh, obj_class_name, obj_class_type))


    return timestamp, local_perception


def cam_to_local_awareness(payload):

    payload = json.loads(payload)
    
    local_awareness = []

    timestamp = payload["cam"]["generationDeltaTime"]
    
    obj_id = payload["header"]["stationId"]

    obj_type = payload["cam"]["camParameters"]["basicContainer"]["stationType"]
    obj_lat = payload["cam"]["camParameters"]["basicContainer"]["referencePosition"]["latitude"]
    obj_lon = payload["cam"]["camParameters"]["basicContainer"]["referencePosition"]["longitude"]

    local_awareness.append((obj_id, obj_type, obj_lat, obj_lon))

    return obj_id,timestamp, local_awareness


def update_ditto_perception(perception):
    global last_local_perception_update

    url = f"{DITTO_BASE_URL}/{DITTO_THING_ID}/features/Perception"
    # Set up headers and basic authentication
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    
    # Send HTTP PUT request to update the twin in Ditto; TODO: Verify status code of response if needed
    #TODO: uncomment (ditto url not working)
    # requests.put(url, headers=headers, auth=(DITTO_USERNAME, DITTO_PASSWORD), json=perception)
    # last_local_perception_update = time.time()


def update_ditto_awareness(awareness):
    global last_local_awareness_update

    url = f"{DITTO_BASE_URL}/{DITTO_THING_ID}/features/Awareness"
    # Set up headers and basic authentication
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    
    # Send HTTP PUT request to update the twin in Ditto; TODO: Verify status code of response if needed
    #TODO: uncomment (ditto url not working)
    # requests.put(url, headers=headers, auth=(DITTO_USERNAME, DITTO_PASSWORD), json=awareness)
    # last_local_awareness_update = time.time()


def update_ditto_dynamics(dynamics):

    url = f"{DITTO_BASE_URL}/{DITTO_THING_ID}/features/Dynamics"
    # Set up headers and basic authentication
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    
    # Send HTTP PUT request to update the twin in Ditto; TODO: Verify status code of response if needed
    #TODO: uncomment (ditto url not working)
    # response = requests.put(url, headers=headers, auth=(DITTO_USERNAME, DITTO_PASSWORD), json=dynamics)
    # if response.status_code in (201, 204):
    #     print("Ditto twin updated successfully.")
    # else:
    #     print(f"Failed to update twin. Status code; {response.status_code}")
    #     print("Response: ", response.text)


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
    global last_local_perception_update

    station_id = message.topic.split("/")[3]

    # if ("MCM" in message.topic):
    #     id, trajectory = obtain_trajectory(message.payload)
    #     update_ditto_trajectories(trajectory)

    #     data_to_send = {"id": id, "trajectory": trajectory}
    #     message_queue.put(json.dumps(data_to_send))

    if (station_id == "22"):
        manage_current_tile(message)
        
        if ("CAM" in message.topic):
            id, dynamics = obtain_dynamics(message.payload)
            update_ditto_dynamics(dynamics)

            data_to_send = {"id": id, "dynamics": dynamics}
            message_queue.put(json.dumps(data_to_send))


    elif (station_id != "22"):
        if ("CPM" in message.topic):
            time_diff = time.time() - last_local_perception_update
            # Check if it has passed at least 1 second since the last ditto update
            if (time_diff < 1):
                return

            timestamp, local_perception = cpm_to_local_perception(message.payload)
            perception = create_perception_json(timestamp, local_perception)
            update_ditto_perception(perception)

            # Send data over websocket
            data_to_send = {"perception":perception}
            message_queue.put(json.dumps(data_to_send))

        elif ("CAM" in message.topic):
            time_diff = time.time() - last_local_awareness_update
            if (time_diff < 10):    #TODO change later for less time to clear, probably
                return
            
            id, timestamp, local_awareness = cam_to_local_awareness(message.payload)
            awareness = create_awareness_json(timestamp, local_awareness)
            update_ditto_awareness(awareness)

            data_to_send = {"id": id, "awareness":awareness}
            message_queue.put(json.dumps(data_to_send))
            


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
            msg = await asyncio.to_thread(message_queue.get)  # Get item from queue
            await send_to_visualizer(msg)

    async def main():
        """Runs both the WebSocket server and the message processor concurrently"""
        await asyncio.gather(websocket_task(), message_processor())

    # Start the event loop properly
    asyncio.run(main())



if __name__ == "__main__":
    # Main thread
    start_agent_thread()