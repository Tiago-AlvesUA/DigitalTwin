import tiles
import json
import time
import global_vars
import math
from ditto_updates import update_ditto_trajectories,update_ditto_perception, update_ditto_awareness, update_ditto_dynamics
from logger import bcolors 
import global_vars


current_original_topic = "placeholder"
current_subscribed_topics = set()
local_awareness = []
local_trajectories = []

own_trajectory = []

def mcm_to_local_trajectory(last_update_time, payload):
    # timestamp = mcm.basicContainer.generationDeltaTime
    # trajectory_points = mcm.mcmContainer.choice.vehiclemaneuverContainer.vehicleTrajectory.choice.wgs84Trajectory.trajectoryPoints
    # for point in trajectory_points:
    #     latitude.append(point.latitudePosition)
    #     longitude.append(point.longitudePosition)

    global local_trajectories

    if (last_update_time > 5):
        local_trajectories = []

    payload = json.loads(payload)

    device_id = payload["header"]["stationId"]
    if (device_id == "22"):
        is_own_vehicle = True
    else:
        is_own_vehicle = False

    timestamp = mcm["basicContainer"]["generationDeltaTime"]

    mcm = payload["mcm"]["mcmContainer"]

    trajectory_points = mcm["choice"]["vehicleManeuverContainer"]["vehicleTrajectory"]["choice"]["wgs84Trajectory"]["trajectoryPoints"]
    
    # Store the trajectory points (lats and longs) as tuples in a list
    local_trajectories = [(point["latitudePosition"], point["longitudePosition"]) for point in trajectory_points]

    return is_own_vehicle, device_id, timestamp, local_trajectories



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



def cam_to_local_awareness(last_update_time, payload):
    global local_awareness

    payload = json.loads(payload)
    
    if (last_update_time > 5):
        local_awareness = []

    timestamp = payload["cam"]["generationDeltaTime"]
    
    obj_id = payload["header"]["stationId"]

    obj_type = payload["cam"]["camParameters"]["basicContainer"]["stationType"]
    obj_lat = payload["cam"]["camParameters"]["basicContainer"]["referencePosition"]["latitude"]
    obj_lon = payload["cam"]["camParameters"]["basicContainer"]["referencePosition"]["longitude"]

    local_awareness.append((obj_id, obj_type, obj_lat, obj_lon))

    return obj_id,timestamp, local_awareness



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



def create_trajectories_json(id, timestamp, local_trajectories):
    objects_json = {
        "properties": {
            "generationDeltaTime": timestamp
        }
    }

    for point in local_trajectories:
        lat, lon = point
        objects_json["properties"][id] = {
            "latitude": lat,
            "longitude": lon
        }

    return objects_json



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
        global_vars.mqtt_client.unsubscribe(topic)

    for topic in topics_to_subscribe:
        #bcolors.log_warning_red(f"Subscribing to new topic: {topic}")
        global_vars.mqtt_client.subscribe(topic)

    current_original_topic = original_topic_path
    current_subscribed_topics = new_subscribed_topics
    for topic in current_subscribed_topics:
        bcolors.log_warning_red(f"Subscribed to topic: {topic}")


def process_message(client, userdata, message):
    station_id = message.topic.split("/")[3]

    # TODO: Differentiate MCMs from the own DT from others? (if station = 22 or not)    
    # if ("MCM" in message.topic):
    #     time_diff = time.time() - global_vars.last_local_trajectories_update

    #     is_own_vehicle, id, timestamp, local_trajectories = mcm_to_local_trajectory(time_diff, message.payload)
    #     if (is_own_vehicle):
    #         own_trajectory = local_trajectories
    #     else: # Check if there are no collisions with other vehicles    
    #         check_for_collisions(own_trajectory, local_trajectories)
        
    #     local_trajectories_json = create_trajectories_json(id, timestamp, local_trajectories)
    #     update_ditto_trajectories(local_trajectories_json)

    #     data_to_send = {"id": id, "trajectory": local_trajectories_json}
        
    #     #global_vars.message_queue.put(json.dumps(data_to_send))

    if (station_id == "22"):
        manage_current_tile(message)
        
        if ("CAM" in message.topic):
            # timestamp is already included in the json in obtain_dynamics()
            id, dynamics = obtain_dynamics(message.payload)
            update_ditto_dynamics(dynamics)

            data_to_send = {"id": id, "dynamics": dynamics}
            global_vars.message_queue.put(json.dumps(data_to_send))


    elif (station_id != "22"):
        if ("CPM" in message.topic):
            time_diff = time.time() - global_vars.last_local_perception_update
            # Check if it has passed at least 1 second since the last ditto update
            if (time_diff < 1):
                return

            timestamp, local_perception = cpm_to_local_perception(message.payload)
            local_perception_json = create_perception_json(timestamp, local_perception)
            update_ditto_perception(local_perception_json)

            # Send data over websocket
            data_to_send = {"perception":local_perception_json}
            global_vars.message_queue.put(json.dumps(data_to_send))

        elif ("CAM" in message.topic):
            global local_awareness
            time_diff = time.time() - global_vars.last_local_awareness_update
            #if (time_diff < 10):    #TODO change later for less time to clear
            #    return
            
            id, timestamp, local_awareness = cam_to_local_awareness(time_diff, message.payload)
            local_awareness_json = create_awareness_json(timestamp, local_awareness)
            update_ditto_awareness(local_awareness_json)

            data_to_send = {"id": id, "awareness":local_awareness_json}
            global_vars.message_queue.put(json.dumps(data_to_send))