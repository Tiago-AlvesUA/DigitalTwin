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

import math


# Calculate interpolated points of a trajectory
def interpolated_points():
    pass


# Haversine formula to calculate the distance between two stations
def stationsDistance(station1, station2):

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


def check_collisions(own_trajectory, other_trajectory):
    collision_detected = False
    
    for i in range(10):
        # Switch 4 to minSafeDistance
        if stationsDistance(own_trajectory[i], other_trajectory[i]) < 4:
            collision_detected = True
            break

        # if (numInterpolatedPoints > 0):
        #     for j in range(numInterpolatedPoints):
        #         if stationsDistance(interpolatedPoints[j], other_trajectory[i]) < 4:
        #             collision_detected = True

    return collision_detected