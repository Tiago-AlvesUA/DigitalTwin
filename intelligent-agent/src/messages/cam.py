import json

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


def cam_to_path_history(payload):
    payload = json.loads(payload)

    cam = payload["cam"]["camParameters"]

    referenceLat = cam["basicContainer"]["referencePosition"]["latitude"]
    referenceLon = cam["basicContainer"]["referencePosition"]["longitude"]

    if "lowFrequencyContainer" in cam:

        path_history = cam["lowFrequencyContainer"]["basicVehicleContainerLowFrequency"]["pathHistory"]

        # Extract the path history points
        path_points = []
        for point in path_history:
            deltaLat = point["pathPosition"]["deltaLatitude"]
            deltaLon = point["pathPosition"]["deltaLongitude"]

            # TODO: Check if i need to divide by 1e7
            lat = referenceLat + deltaLat
            lon = referenceLon + deltaLon

            path_points.append((lat/1e7, lon/1e7))

            referenceLat = lat
            referenceLon = lon

        return path_points
    
    else:
        return []

# When i get path history already from ditto, feature Dynamics
def delta_path_history_to_coordinates(path_history, reference_position):
    referenceLat = reference_position[0]
    referenceLon = reference_position[1]

    path_points = []
    for point in path_history:
        deltaLat = point["pathPosition"]["deltaLatitude"]
        deltaLon = point["pathPosition"]["deltaLongitude"]

        # TODO: Check if i need to divide by 1e7
        lat = referenceLat + deltaLat
        lon = referenceLon + deltaLon

        path_points.append((lat/1e7, lon/1e7))

        referenceLat = lat
        referenceLon = lon

    return path_points



def cam_to_local_awareness(last_update_time, payload):
    payload = json.loads(payload)

    #global local_awareness
    # TODO: Change if necessary
    if "lowFrequencyContainer" in payload["cam"]["camParameters"]:
        path_history = payload["cam"]["camParameters"]["lowFrequencyContainer"]["basicVehicleContainerLowFrequency"]["pathHistory"]
    #path_history = cam_to_path_history(payload)
    else:
        path_history = []

    #if (last_update_time > 5):
    #    local_awareness = []
    local_awareness = []

    timestamp = payload["cam"]["generationDeltaTime"]

    #print(f"Payload: {payload}")

    #obj_id = payload["header"]["stationId"]
    header = payload.get("header", {})
    obj_id = header.get("stationId") or header.get("stationID")
    if not obj_id:
        return

    obj_type = payload["cam"]["camParameters"]["basicContainer"]["stationType"]
    obj_lat = payload["cam"]["camParameters"]["basicContainer"]["referencePosition"]["latitude"]
    obj_lon = payload["cam"]["camParameters"]["basicContainer"]["referencePosition"]["longitude"]

    local_awareness.append((obj_id, obj_type, obj_lat, obj_lon, path_history))

    return obj_id, timestamp, local_awareness


def create_awareness_json(timestamp, local_awareness):
    objects_json = {
        "properties": {
            "generationDeltaTime": timestamp
        }
    }

    for obj in local_awareness:
        id, type, lat, lon, path_history = obj
        objects_json["properties"][id] = {
            "stationType": type,
            "latitude": lat,
            "longitude": lon,
            "pathHistory": path_history
        }

    return objects_json