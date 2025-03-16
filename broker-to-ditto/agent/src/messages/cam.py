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



def cam_to_local_awareness(last_update_time, payload):
    #global local_awareness

    payload = json.loads(payload)
    
    #if (last_update_time > 5):
    #    local_awareness = []
    local_awareness = []

    timestamp = payload["cam"]["generationDeltaTime"]
    
    obj_id = payload["header"]["stationId"]

    obj_type = payload["cam"]["camParameters"]["basicContainer"]["stationType"]
    obj_lat = payload["cam"]["camParameters"]["basicContainer"]["referencePosition"]["latitude"]
    obj_lon = payload["cam"]["camParameters"]["basicContainer"]["referencePosition"]["longitude"]

    local_awareness.append((obj_id, obj_type, obj_lat, obj_lon))

    return obj_id, timestamp, local_awareness


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