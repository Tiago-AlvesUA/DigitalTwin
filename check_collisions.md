## How to check for vehicle collisions

In order to detect the collisions multiple physical simulations were created.

They predict the future trajectory of a vehicle based on the vehicle's current position, speed and heading. The trajectory predicted is 3 seconds long, and every simulation occurs within 1 second difference.

The vehicles (represented by small rectangles in the simulation) will drive, according to a speed that rectangle/object has. In this driving interval the algorithm checks for collisions between the vehicles. The speed is what creates the "trajectory" that the vehicle realizes.

In addition, not done yet, there is an apply_force function that allows to use acceleration to apply a certain force at a local point. This force can either reduce or increase the speed of the vehicle. 