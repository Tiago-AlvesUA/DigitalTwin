import math
import json
from dataclasses import dataclass

@dataclass
class Coordinates:
    latitude: float
    longitude: float
    heading: float

local_trajectories = []


def create_trajectories_json(id, timestamp, local_trajectories):
    objects_json = {
        "properties": {
            "generationDeltaTime": timestamp,
            id: []
        }
    }

    if local_trajectories != []:

        #print(local_trajectories)
        for point in local_trajectories:
            if point == 0:
                continue
            objects_json["properties"][id].append({
                "latitude": point.latitude,
                "longitude": point.longitude,
                "heading": point.heading
            })

    return objects_json


def mcm_to_local_trajectory(last_update_time, payload):
    global local_trajectories

    # TODO: Add clearing of local_trajectories
    #if (last_update_time > 5):
    #    local_trajectories = []

    payload = json.loads(payload)

    device_id = payload["header"]["stationId"]
    timestamp = payload["payload"]["basicContainer"]["generationDeltaTime"]

    referenceLat = payload["payload"]["basicContainer"]["referencePosition"]["latitude"]
    referenceLon = payload["payload"]["basicContainer"]["referencePosition"]["longitude"]

    mcm = payload["payload"]["mcmContainer"]
    referenceHeading = mcm["vehiclemaneuverContainer"]["vehicleCurrentState"]["heading"]["headingValue"]
    speed = mcm["vehiclemaneuverContainer"]["vehicleCurrentState"]["speed"]["speedValue"]
    trajectory_points = mcm["vehiclemaneuverContainer"]["vehicleTrajectory"]["wgs84Trajectory"]["trajectoryPoints"]
    
    referenceLatPoint = referenceLat
    referenceLonPoint = referenceLon

    trajectory = []

    for intermeadiatePoint in trajectory_points:
        referenceHeadingPoint = intermeadiatePoint["intermediatePoint"]["reference"]["referenceHeading"]["headingValue"]
        
        deltaLat = intermeadiatePoint["intermediatePoint"]["reference"]["deltaReferencePosition"]["deltaLatitude"]
        deltaLon = intermeadiatePoint["intermediatePoint"]["reference"]["deltaReferencePosition"]["deltaLongitude"]

        lat = referenceLatPoint + deltaLat
        lon = referenceLonPoint + deltaLon

        trajectory.append(Coordinates(lat,lon,referenceHeadingPoint))

        referenceLatPoint = lat
        referenceLonPoint = lon


    return device_id, timestamp, speed, referenceLat, referenceLon, referenceHeading, trajectory #, local_trajectories
