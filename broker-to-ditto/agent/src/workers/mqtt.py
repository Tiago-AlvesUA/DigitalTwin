from utils.tiles import It2s_Tiles
import asyncio
import json
import time
import paho.mqtt.client as mqtt
from config import BROKER_HOST, BROKER_PORT, MQTT_USERNAME, MQTT_PASSWORD, MQTT_INITIAL_TOPIC
from utils.ditto import update_ditto_trajectories, update_ditto_perception, update_ditto_awareness, update_ditto_dynamics
from utils.logger import bcolors 
from messages.cpm import cpm_to_local_perception, create_perception_json
from messages.cam import obtain_dynamics, cam_to_local_awareness, create_awareness_json
from messages.mcm import mcm_to_local_trajectory, create_trajectories_json, check_collisions
# TODO: remove GLOBAL VARS and switch for a shared memory or queue with an interface
#import global_vars
from workers.shared_memory import messages

current_original_topic = "placeholder"
current_subscribed_topics = set()
#local_awareness = []        # TODO
#local_trajectories = []         # TODO

own_trajectory = [] # TODO: Not used anymore

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport='websockets')

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

    it2s_tiles = It2s_Tiles()
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
    station_id = message.topic.split("/")[3]

    # TODO: Differentiate MCMs from the own DT from others? (if station = 22 or not)    
    # if ("MCM" in message.topic):
    #     time_diff = time.time() - global_vars.last_local_trajectories_update

    #     is_own_vehicle, id, timestamp, local_trajectories = mcm_to_local_trajectory(time_diff, message.payload)
    #     if (is_own_vehicle):
    #         own_trajectory = local_trajectories
    #     else: # Check if there are no collisions with other vehicles    
    #         check_collisions(own_trajectory, local_trajectories)
        
    #     local_trajectories_json = create_trajectories_json(id, timestamp, local_trajectories)
    #     update_ditto_trajectories(local_trajectories_json)

    #     data_to_send = {"id": id, "trajectory": local_trajectories_json}
    #     global_vars.message_queue.put(json.dumps(data_to_send))

    if (station_id == "22"):
        if ("CAM" in message.topic):
            # Now switched management of current tile here, because MCMs do not have the tile path
            manage_current_tile(message)

            # timestamp is already included in the json in obtain_dynamics()
            id, dynamics = obtain_dynamics(message.payload)
            update_ditto_dynamics(dynamics)

            data_to_send = {"id": id, "dynamics": dynamics}
            #SharedQueue.add_message(json.dumps(data_to_send))
            #add_message_to_queue(json.dumps(data_to_send))
            messages.put(json.dumps(data_to_send))
            #global_vars.message_queue.put(json.dumps(data_to_send))

        # TODO: Change for below (MCMs must be received by other stations)
        elif ("MCM" in message.topic):
            dummy = 0
            # Other vehicle trajectory
            id, timestamp, sender_trajectory = mcm_to_local_trajectory(dummy, message.payload)
            
            exists_collision = check_collisions(sender_trajectory)

            # Local trajectories will track trajectories close to the vehicle
            local_trajectories_json = create_trajectories_json(id, timestamp, sender_trajectory)
            update_ditto_trajectories(local_trajectories_json)

            data_to_send = {"id": id, "trajectory": local_trajectories_json}
            messages.put(json.dumps(data_to_send))

    elif (station_id != "22"):
        if ("CPM" in message.topic):
            #time_diff = time.time() - global_vars.last_local_perception_update
            # Check if it has passed at least 1 second since the last ditto update
            #if (time_diff < 1):
            #    return

            timestamp, local_perception = cpm_to_local_perception(message.payload)
            local_perception_json = create_perception_json(timestamp, local_perception)
            update_ditto_perception(local_perception_json)

            # Send data over websocket
            data_to_send = {"perception":local_perception_json}
            #SharedQueue.add_message(json.dumps(data_to_send))
            #put_message(json.dumps(data_to_send))
            messages.put(json.dumps(data_to_send))
            #global_vars.message_queue.put(json.dumps(data_to_send))

        elif ("CAM" in message.topic):
            #global local_awareness
            #time_diff = time.time() - global_vars.last_local_awareness_update
            #if (time_diff < 10):    #TODO change later for less time to clear
            #    return
            dummy = 0
            id, timestamp, local_awareness = cam_to_local_awareness(dummy, message.payload)
            local_awareness_json = create_awareness_json(timestamp, local_awareness)
            update_ditto_awareness(local_awareness_json)

            data_to_send = {"id": id, "awareness":local_awareness_json}
            #SharedQueue.add_message(json.dumps(data_to_send))
            #put_message(json.dumps(data_to_send))
            messages.put(json.dumps(data_to_send))
            #global_vars.message_queue.put(json.dumps(data_to_send))
    
            
 

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
    mqtt_client.loop_forever()
