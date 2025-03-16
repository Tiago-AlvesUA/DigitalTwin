# Obter ambas as trajetórias tanto do próprio DT quanto do outro veículo
# Para isto basta obter ambas as MCMs

# TODO (duvida): Não sei se deverei mudar a forma no message_processing.py como eu recebo as mensagens MCMs
# A trajetória do veículo deve ser sempre comparada à dos outros veículos

# Portanto devo de ter de guardar a trajetória do veículo à parte
# E comparar com as restantes trajetórias

# TODO (duvida): Como vai ser com os timestamps das MCMs? Porque um ponto de uma MCM de um veículo talvez 
# não coincida com o ponto de outra MCM de outro veículo 
# TODO: Tenho de comparar timestamps dos pontos das MCMs (incluindo interpolados) para verificar
# se são pontos correspondentes em termos de tempo?

# TODO: Preciso de verificar as lanes / sub-lanes para vver se posso comparar
# as trajetórias dos veículos?


# TODO: Cada vez que recebo uma MCM de outro veículo, tenho de calcular a trajetória
# do próprio veículo antes e depois verificar se há colisões coma do outro carro
# (assim os timestamps dos pontos das trajetórias dos veículos têm de ser iguais)

import math
import json
import requests
from dataclasses import dataclass
from config import DITTO_BASE_URL, DITTO_THING_ID, DITTO_USERNAME, DITTO_PASSWORD
from utils.ditto import get_dynamics

@dataclass
class Coordinates:
    latitude: float
    longitude: float
    heading: float


local_trajectories = []


def linear_intermediate_points(idx, latitude, longitude, heading, speed):

    speed = speed * 1e-2 # Convert speed to m/s
    # TODO: Why use index?
    distance = speed * idx * 0.5 # Calculate distance a vehicle can travel in 0.5 second

    # Convert values to radians
    latitude = latitude * 1e-7 * math.pi/180 
    longitude = longitude * 1e-7 * math.pi/180 
    heading = heading * 1e-1 * math.pi/180

    R = 6371e3 # Earth radius in meters
    
    # Calculate new latitude and longitude: https://www.movable-type.co.uk/scripts/latlong.html (Destination point given distance and bearing from start point)
    latitude = math.asin(math.sin(latitude) * math.cos(distance/R) + math.cos(latitude) * math.sin(distance/R) * math.cos(heading))
    longitude = longitude + math.atan2(math.sin(heading) * math.sin(distance/R) * math.cos(latitude), math.cos(distance/R) - math.sin(latitude) * math.sin(latitude))
    # heading stays the same

    # Convert values back to degrees
    latitude = latitude * 1e7 * 180/math.pi
    longitude = longitude * 1e7 * 180/math.pi
    heading = heading * 1e1 * 180/math.pi

    #print(f"Latitude: {latitude}, Longitude: {longitude}, Heading: {heading}, Speed: {speed}")

    return (latitude, longitude)


# Calculate interpolated points of a trajectory
def interpolated_points():
    pass


# Haversine formula to calculate the distance between two stations
def stations_distance(station1, station2):

    R = 6371e3 # Earth radius in meters

    lat1, lon1 = station1
    lat2, lon2 = station2 

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(a ** 0.5, (1 - a) ** 0.5)

    return R * c


def check_collisions(sender_trajectory):
    collision_detected = False
    
    print(f"Sender Trajectory: {sender_trajectory}\n")

    # First collect necessary data to calculate the own trajectory
    current_dynamics = get_dynamics()
    
    latitude = current_dynamics["properties"]["basicContainer"]["referencePosition"]["latitude"]
    longitude = current_dynamics["properties"]["basicContainer"]["referencePosition"]["longitude"]
    heading = current_dynamics["properties"]["highFrequencyContainer"]["heading"]["headingValue"]
    speed = current_dynamics["properties"]["highFrequencyContainer"]["speed"]["speedValue"]
    
    receiver_trajectory = [0] * 10
    # TODO:
    for i in range(10):
        receiver_trajectory[i] = linear_intermediate_points(i, latitude, longitude, heading, speed)

    print(f"Receiver Trajectory: {receiver_trajectory}\n")
    # for i in range(10):
    #     # Switch 4 to minSafeDistance
    #     if stations_distance(own_trajectory[i], other_trajectory[i]) < 4:
    #         collision_detected = True
    #         break

        # if (numInterpolatedPoints > 0):
        #     for j in range(numInterpolatedPoints):
        #         if stationsDistance(interpolatedPoints[j], other_trajectory[i]) < 4:
        #             collision_detected = True

    return collision_detected


def create_trajectories_json(id, timestamp, local_trajectories):
    objects_json = {
        "properties": {
            "generationDeltaTime": timestamp,
            id: []
        }
    }

    for point in local_trajectories:
        lat, lon = point
        objects_json["properties"][id].append({
            "latitude": lat,
            "longitude": lon
        })

    return objects_json


def mcm_to_local_trajectory(last_update_time, payload):
    # timestamp = mcm.basicContainer.generationDeltaTime
    # trajectory_points = mcm.mcmContainer.choice.vehiclemaneuverContainer.vehicleTrajectory.choice.wgs84Trajectory.trajectoryPoints
    # for point in trajectory_points:
    #     latitude.append(point.latitudePosition)
    #     longitude.append(point.longitudePosition)

    global local_trajectories

    #if (last_update_time > 5):
    #    local_trajectories = []

    payload = json.loads(payload)

    device_id = payload["header"]["stationId"]

    mcm = payload["payload"]["mcmContainer"]

    timestamp = payload["payload"]["basicContainer"]["generationDeltaTime"]

    trajectory_points = mcm["vehiclemaneuverContainer"]["vehicleTrajectory"]["wgs84Trajectory"]["trajectoryPoints"]

    # Store the trajectory points (lats and longs) as tuples in a list
    # TODO: Use local_trajectories list to append, and trajectory to only store the last trajectory
    #local_trajectories = [(point["latitudePosition"], point["longitudePosition"]) for point in trajectory_points]
    trajectory = [(point["latitudePosition"], point["longitudePosition"]) for point in trajectory_points]

    #print("Local Trajectories: ", local_trajectories)

    return device_id, timestamp, trajectory #, local_trajectories
