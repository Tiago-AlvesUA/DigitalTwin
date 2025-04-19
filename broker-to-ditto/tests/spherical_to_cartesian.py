import numpy as np
import matplotlib.pyplot as plt
import pytransform3d.plot_utils as ppu
from distance3d.distance import rectangle_to_rectangle
from distance3d import plotting
from pyproj import Proj, Transformer
import utm

# # Rectangle 1
# # TODO: Pode equivaler à posição do carro (latitude e longitude)
# center1 = np.array([0.0, 0.0, 0.0])  # XYZ position
# axes1 = np.eye(3)  # Identity matrix = aligned to world axes
# # TODO: Tem de corresponder aos tamanhos do carro (largura e comprimento)
# lengths1 = np.array([2.0, 1.0, 0.0])  # width, height, depth

# # Rectangle 2
# center2 = np.array([3.0, 1.0, 0.0])  # offset in XY plane
# axes2 = np.eye(3)  # also aligned to world axes
# lengths2 = np.array([1.5, 1.0, 0.0])  # width, height, depth

# # Compute distance between them
# distance, closest_point1, closest_point2 = rectangle_to_rectangle(
#     center1, axes1, lengths1,
#     center2, axes2, lengths2
# )

# print("Distance:", distance)
# print("Closest point on rectangle 1:", closest_point1)
# print("Closest point on rectangle 2:", closest_point2)

# # Plot
# ax = ppu.make_3d_axis(ax_s=3)
# plotting.plot_rectangle(ax, center1, axes1, lengths1, show_axes=True)
# plotting.plot_rectangle(ax, center2, axes2, lengths2, show_axes=True)
# plotting.plot_segment(ax, closest_point1, closest_point2, c="red", lw=2)

# plt.title(f"Distance = {distance:.3f}")
# plt.show()

# TODO: the refence position can be own vehicle ref position (the rest of the positions in the trajectory of the vehicle will be compared using that (0,0) reference) 
# def latlon_to_enu(lat, lon, ref_lat, ref_lon):
#     # first projection type
#     proj_lla = Proj(proj="latlong",datum="WGS84")

#     utm_zone = int((ref_lon + 180) / 6) + 1 # Should be 29
#     print(utm_zone)
#     # second projection type
#     proj_utm = Proj(proj="utm", zone=utm_zone, datum="WGS84")

#     # Create transformer objet with the both projections
#     transformer = Transformer.from_proj(proj_lla, proj_utm)

#     x, y = transformer.transform(lat, lon)
#     x_ref, y_ref = transformer.transform(ref_lat, ref_lon)

#     return np.array([x - x_ref, y - y_ref, 0.0])

def latlon_to_local(lat, lon):
    # Transformer from WGS84 (EPSG:4326) to Portugal TM06 (EPSG:3763)
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3763", always_xy=True)
    
    x, y = transformer.transform(lon, lat)  # Note: Always (lon, lat) order for pyproj
    return np.array([x, y, 0.0])

def main():
    refpos = (40.6337703, -8.6786889)
    v1_latlon = (40.6337703, -8.6786889)
    v2_latlon = (40.6337449, -8.6786678)

    # center1 = np.array([40.6338707,-8.6781110,0.0])
    # center2 = np.array([40.6257824, -8.7203087,0.0])

    # flat coords of the center of the vehicle
    # flat_coord1 = latlon_to_enu(*v1_latlon, *refpos)
    flat_coord1 = latlon_to_local(*v1_latlon)
    print(flat_coord1)
    # flat_coord2 = latlon_to_enu(*v2_latlon,*refpos)
    flat_coord2 = latlon_to_local(*v2_latlon)
    print(flat_coord2)

    coorUTM1 = utm.from_latlon(*v1_latlon)
    coorUTM2 = utm.from_latlon(*v2_latlon)
    print(coorUTM1)
    print(coorUTM2)

    axes1 = np.eye(3)
    axes2 = np.eye(3)

    length1 = np.array([2.0, 1.0, 0.0])
    length2 = np.array([2.0, 1.0, 0.0])

    distance, closest_point1, closest_point2 = rectangle_to_rectangle(
    flat_coord1, axes1, length1,
    flat_coord2, axes2, length2
    # center1,axes1,length1,
    # center2,axes2,length2
    )

    print("Distance:", distance)

    distance2, closest_point1, closest_point2 = rectangle_to_rectangle(
    np.array([coorUTM1[0],coorUTM1[1],0.0]), axes1, length1,
    np.array([coorUTM2[0],coorUTM2[1],0.0]), axes2, length2
    )
    print("Distance:", distance2)
    print()
    print()

    distance3, closest_point1, closest_point2 = rectangle_to_rectangle(
    np.array([0.0,0.0,0.0]), axes1, length1,
    np.array([1.7946300170151517,-2.8129515359178185,0.0]), axes2, length2
    )
    print("Distance:", distance3)

if __name__ == "__main__":
    main()
