import numpy as np
import matplotlib.pyplot as plt
import pytransform3d.plot_utils as ppu
from distance3d.distance import rectangle_to_rectangle
from distance3d import plotting

# Rectangle 1
# TODO: Pode equivaler à posição do carro (latitude e longitude)
center1 = np.array([0.0, 0.0, 0.0])  # XYZ position
axes1 = np.eye(3)  # Identity matrix = aligned to world axes
# TODO: Tem de corresponder aos tamanhos do carro (largura e comprimento)
lengths1 = np.array([2.0, 1.0, 0.0])  # width, height, depth

# Rectangle 2
center2 = np.array([3.0, 1.0, 0.0])  # offset in XY plane
axes2 = np.eye(3)  # also aligned to world axes
lengths2 = np.array([1.5, 1.0, 0.0])  # width, height, depth

# Compute distance between them
distance, closest_point1, closest_point2 = rectangle_to_rectangle(
    center1, axes1, lengths1,
    center2, axes2, lengths2
)

print("Distance:", distance)
print("Closest point on rectangle 1:", closest_point1)
print("Closest point on rectangle 2:", closest_point2)

# Plot
ax = ppu.make_3d_axis(ax_s=3)
plotting.plot_rectangle(ax, center1, axes1, lengths1, show_axes=True)
plotting.plot_rectangle(ax, center2, axes2, lengths2, show_axes=True)
plotting.plot_segment(ax, closest_point1, closest_point2, c="red", lw=2)

plt.title(f"Distance = {distance:.3f}")
plt.show()
