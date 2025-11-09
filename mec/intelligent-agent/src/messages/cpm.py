import json
import math

# NOTE: Distinguish CPM versions if necessary
def cpm_to_local_perception(payload):
    payload = json.loads(payload)

    # TODO: Change the way local perception is cleared. Right now it is cleared every time a new CPM is received.
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
