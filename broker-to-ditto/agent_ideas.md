## Cooperative Maneuver handling

In order to check for collisions between two trajectories, the agent of the vehicle receives different C-ITS messages. Specifically, when it receives a MCM from another vehicle, it will retire the trajectory from it to compare it to the own agent vehicle. To do so, the own vehicle trajectory is calculated in the moment the MCM is received, getting the current coordinates from Ditto's Dynamics feature (a feature that is updated by the agent, using the vehicle's CAMs).

To calculate the own vehicle trajectory, alongside the coordinates (latitude and longitude), i also need the heading and speed.

After i have both trajectories i need to calculate the interpolated points for both sender and receiver. If one has speed higher than other, the number of interpolated points will be affected.

After i obtain those values, convert speed to m/s, and the other variables (lat, lon, heading) to radians. This is to calculate the destination point given distance and bearing (using heading in this case) from a start point. Most of the mathematical functions expect angles in radians, not degrees.