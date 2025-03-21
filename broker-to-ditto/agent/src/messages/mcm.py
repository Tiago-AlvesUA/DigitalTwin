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
from workers.shared_memory import messages

@dataclass
class Coordinates:
    latitude: float
    longitude: float
    heading: float

class VehicleInfo:
    def __init__(self, id, distance, speed):
        self.id = id
        self.intermediatePointsDistance = distance
        self.speed = speed

    def get_id(self):
        return self.id
    
    def get_distance(self):
        return self.intermediatePointsDistance
    
    def get_speed(self):
        return self.speed
        

local_trajectories = []


def linear_intermediate_points(idx, latitude, longitude, heading, speed):

    speed = speed * 1e-2 # Convert speed to m/s
    # Uses index because each intermediate point is calculated based on the current position (and not on the point before)
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

    return (int(latitude), int(longitude))


# Calculate interpolated points of a trajectory
def interpolated_points():
    pass


# Haversine formula to calculate the distance between two stations
def stations_distance(station1_point, station2_point):

    R = 6371e3 # Earth radius in meters

    lat1, lon1 = station1_point
    lat2, lon2 = station2_point 

    phi1 = lat1 * 1e-7 * math.pi/180
    phi2 = lat2 * 1e-7 * math.pi/180
    delta_phi = (lat2 - lat1) * 1e-7 * math.pi/180
    delta_lambda = (lon2 - lon1) * 1e-7 * math.pi/180

    # phi1 = math.radians(lat1)
    # phi2 = math.radians(lat2)
    # delta_phi = math.radians(lat2 - lat1)
    # delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(a ** 0.5, (1 - a) ** 0.5)

    return R * c # Distance in meters


def check_collisions(sender_id, sender_speed, sender_trajectory):
    ## TODO ## TODO ## ## TODO ## TODO ## ## TODO ## TODO ##
    # Sender trajectory now contains points with heading value -> Create arrays of 10, each position using coordinates class
    ## TODO ## TODO ## ## TODO ## TODO ## ## TODO ## TODO ##

    #### SENDER DATA ####
    sender_vehicle = VehicleInfo(sender_id, sender_speed * 1e-2 * 0.5, sender_speed)
    #####################

    collision_detected = False
    
    # TODO: Preencher distância entre pontos do sender como? A distância entre pontos é sempre a mesma? Assim posso ir buscar a distância a partir da velocidade que é constante
    # sender = Vehicle(sender_id, sender_distance, sender_speed)
    
    #print(f"Sender Trajectory: {sender_trajectory}\n")

    # TODO: Check if can get the dynamics from ditto or if i have to obtain them from the data reader
    # First collect necessary data to calculate the own trajectory
    ###current_dynamics = get_dynamics()
    
    #### RECEIVER DATA ####
    ###latitude = current_dynamics["properties"]["basicContainer"]["referencePosition"]["latitude"]
    ###longitude = current_dynamics["properties"]["basicContainer"]["referencePosition"]["longitude"]
    ###heading = current_dynamics["properties"]["highFrequencyContainer"]["heading"]["headingValue"]
    ###speed = current_dynamics["properties"]["highFrequencyContainer"]["speed"]["speedValue"]
    
    ###receiver_vehicle = VehicleInfo(22, speed * 1e-2 * 0.5, speed)
    receiver_vehicle = VehicleInfo(22, 2501 * 1e-2 * 0.5, 2501)

    receiver_trajectory = [0] * 10

    for i in range(10):
        ###receiver_trajectory[i] = linear_intermediate_points(i, latitude, longitude, heading, speed)
        # TODO: uncomment - doing with dummy values before having connection to the 
        #receiver_trajectory[i] = linear_intermediate_points(i, latitude, longitude, heading, speed)
        receiver_trajectory[i] = linear_intermediate_points(i, 406294531, -87366649, 2899, 2500) # DUMMY values -> TODO: to remove

    data_to_send = {"id": 23, "receiverTrajectory": receiver_trajectory}
    messages.put(json.dumps(data_to_send))
    #######################


    # TODO: Before calculating, check if distance between points for sender or receiver is bigger than 2 meters
    numInterpolatedPoints = 0
    maxInterpolatedPointsDistance = 2 # TODO: Distância configurável (e não apenas 2 metros)

    # Number of interpolated points calculated of the higher speed
    if sender_vehicle.get_speed() > receiver_vehicle.get_speed():
        if sender_vehicle.get_distance > 2: # only calculate interpolated points if distance between intermediate points is bigger than 2 meters
            numInterpolatedPoints = math.floor(sender_vehicle.get_distance()/maxInterpolatedPointsDistance)
    else:
        if receiver_vehicle.get_distance() > 2:
            numInterpolatedPoints = math.floor(receiver_vehicle.get_distance()/maxInterpolatedPointsDistance)

    print(numInterpolatedPoints)

    # TODO TODO TODO TODO
    # TODO: - Get senderCoordinates and receiverCoordinates(reference position)
    #if numInterpolatedPoints > 0:
        # sender trajectory is the equivalent to senderIntermediatePointsCoor (without the heading)
        #interpolated_points(numInterpolatedPoints, maxInterpolatedPointsDistance, sender_vehicle.get_distance(), sender_vehicle.get_id(), sender_vehicle.get_speed(), senderCoordinates, sender_trajectory)

    # # print(f"Receiver Trajectory: {receiver_trajectory}\n")
    # for i in range(10):
    #     # Switch 4 to minSafeDistance
    #     if stations_distance(receiver_trajectory[i], sender_trajectory[i]) < 4:
    #         print(f"Collision detected between receiver and sender at point {i}")
    #         print(f"latitude: {receiver_trajectory[i][0]}, longitude: {receiver_trajectory[i][1]}")
    #         print(f"latitude: {sender_trajectory[i][0]}, longitude: {sender_trajectory[i][1]}")
    #         collision_detected = True
    #         break
    #     #else:
    #         #print(f"Stations distance: {stations_distance(receiver_trajectory[i], sender_trajectory[i])}")

    #     # if (numInterpolatedPoints > 0):
    #     #     for j in range(numInterpolatedPoints):
    #     #         if stationsDistance(interpolatedPoints[j], other_trajectory[i]) < 4:
    #     #             collision_detected = True

    return collision_detected


def create_trajectories_json(id, timestamp, local_trajectories):
    objects_json = {
        "properties": {
            "generationDeltaTime": timestamp,
            id: []
        }
    }

    # TODO: Modify to also include hreading values of the intermediate points

    if local_trajectories != []:

        print(local_trajectories)
        for point in local_trajectories:
            if point == 0:
                continue
            lat, lon, heading = point
            objects_json["properties"][id].append({
                "latitude": lat,
                "longitude": lon,
                "heading": heading
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
    timestamp = payload["payload"]["basicContainer"]["generationDeltaTime"]

    #################
    referenceLat = payload["payload"]["basicContainer"]["referencePosition"]["latitude"]
    referenceLon = payload["payload"]["basicContainer"]["referencePosition"]["longitude"]

    mcm = payload["payload"]["mcmContainer"]

    speed = mcm["vehiclemaneuverContainer"]["vehicleCurrentState"]["speed"]["speedValue"]

    trajectory_points = mcm["vehiclemaneuverContainer"]["vehicleTrajectory"]["wgs84Trajectory"]["trajectoryPoints"]
    # Store the trajectory points (lats and longs) as tuples in a list
    # TODO: Use local_trajectories list to append, and trajectory to only store the last trajectory
    # TODO: Change obtaining of lat and lon (use delta lat and delta lon)
    #local_trajectories = [(point["latitudePosition"], point["longitudePosition"]) for point in trajectory_points]
    #trajectory = [(point["latitudePosition"], point["longitudePosition"]) for point in trajectory_points]
    trajectory = [0] * 10
    i=0
    for intermeadiatePoint in trajectory_points:
        referenceHeading = intermeadiatePoint["intermediatePoint"]["reference"]["referenceHeading"]["headingValue"]
        
        deltaLat = intermeadiatePoint["intermediatePoint"]["reference"]["deltaReferencePosition"]["deltaLatitude"]
        deltaLon = intermeadiatePoint["intermediatePoint"]["reference"]["deltaReferencePosition"]["deltaLongitude"]

        lat = referenceLat + deltaLat
        lon = referenceLon + deltaLon

        trajectory[i] = (lat,lon,referenceHeading)

        referenceLat = lat
        referenceLon = lon

        i = i+1

    #print("Local Trajectories: ", local_trajectories)

    return device_id, timestamp, speed, trajectory #, local_trajectories
