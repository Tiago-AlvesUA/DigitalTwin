import math
import requests
from workers.ditto_listener import get_dynamics
import pymunk
import pymunk.pygame_util
from workers.visualizer import latlon_to_img_pixel, position_of_vehicle, get_window_surface, get_window_dimensions, restore_background, export_final_frame, create_collision_visualizer
from pyquadkey2 import quadkey
import time

current_awareness = None
time_elapsed = 0.0
collision_time = None

def compass_to_trigonometric_angle(degrees_heading):
    return math.radians(90 - degrees_heading)

def apply_force(vehicle, acceleration):
    force = vehicle.mass * acceleration # F = m * a (Newton's second law)
    heading = vehicle.angle

    force_x = force * math.cos(heading)
    force_y = force * math.sin(heading)

    vehicle.apply_force_at_local_point((force_x,force_y), (0,0))    # Always applied at position (0,0) since it is the Center of Mass of the object (it already takes in consideration the coordinates where the object is)

def create_vehicle(space, position, mass, width, length, heading, speed, color):
    # Since pymunk does not care about length, it just draws a rectangle where width is aligned with the x-axis and height with the y-axis, we need to switch width and length
    box_width = length
    box_height = width
    body = pymunk.Body(mass, pymunk.moment_for_box(mass, (box_width, box_height))) # Moment for box calculates moment of intertia, which is necessary to determine resistance to rotational motion (and behave more realistically)

    position = position_of_vehicle(position[0],position[1])

    body.position = position
    body.angle = heading
    # Using initial speed to calculate velocity
    velocity_x = speed * math.cos(heading)
    velocity_y = speed * math.sin(heading)
    body.velocity = (velocity_x, velocity_y)

    # pymunk.Poly is a convex polygon shape
    shape = pymunk.Poly.create_box(body, (width, length))
    shape.mass = mass
    shape.collision_type = 1
    shape.color = color 

    space.add(body, shape)
    return body, shape

def draw(space, draw_options):
    space.debug_draw(draw_options)

def collision_handler(arbiter, space, data):
    global collision_time, time_elapsed
    collision_time = time_elapsed
    print(f"Collision detected at {collision_time:.2f} seconds!")
    return True

def check_collisions(sender_id, sender_speed, sender_lat, sender_lon, sender_heading, sender_trajectory):
    global collision_time, time_elapsed
    
    time_overall = time.time()  # Start timer for performance measurement

    time_elapsed = 0.0
    collision_time = None

    fps = 60
    dt = 1/fps

    space = pymunk.Space()
    space.gravity = (0,0)

    collision_detected = False

    # Collect receiver information (dynamics)
    current_dynamics = get_dynamics()

    # If there are no dynamics yet, can not do the collision check
    if current_dynamics == None:
        print("No dynamics yet from own vehicle to check for collisions.")
        return collision_detected, 21

    #### RECEIVER DATA #### TODO: No need to get ID from the vehicle since i already get it from the toml file (?)
    receiver_lat = current_dynamics["properties"]["basicContainer"]["referencePosition"]["latitude"]
    receiver_lon = current_dynamics["properties"]["basicContainer"]["referencePosition"]["longitude"]
    receiver_heading = current_dynamics["properties"]["highFrequencyContainer"]["heading"]["headingValue"]
    receiver_speed = current_dynamics["properties"]["highFrequencyContainer"]["speed"]["speedValue"]
    receiver_id = 21 # DUMMY, should get from toml file

    # Draws background map and path histories of vehicles in pygame
    create_collision_visualizer(current_dynamics, receiver_lat, receiver_lon, sender_id, sender_lat, sender_lon)
    # Get pygame surfaces and values
    WIDTH, HEIGHT = get_window_dimensions()
    window = get_window_surface()

    # Transform spherical coordinates into the pixel position in the visualization map
    sender_position = latlon_to_img_pixel(sender_lat/1e7,sender_lon/1e7)
    receiver_position = latlon_to_img_pixel(receiver_lat/1e7,receiver_lon/1e7)
   
    # Heading comes in compass degrees, so we need to convert it to a trigonometric angle
    sender_heading = compass_to_trigonometric_angle(sender_heading/10)
    receiver_heading = compass_to_trigonometric_angle(receiver_heading/10)

    # Create bodies for the vehicles in the simulation
    sender_body, sender_shape = create_vehicle(space, sender_position, 10, 1.8, 4.3, sender_heading, sender_speed*1e-2, color=(0, 0, 255, 255)) # blue
    receiver_body, receiver_shape = create_vehicle(space, receiver_position, 10, 1.8, 4.3, receiver_heading, receiver_speed*1e-2, color=(255, 0, 0, 255)) # red

    collision = space.add_collision_handler(1,1)  # Type 1 = Cars
    collision.begin = collision_handler

    draw_options = pymunk.pygame_util.DrawOptions(window)
    # Flip Y-axis, since pygame origin is at the top left corner
    # Also, translate the origin to the center of the screen
    flip_y = pymunk.Transform(a=1, b=0, c=0, d=-1, tx=WIDTH // 2, ty=HEIGHT // 2)
    draw_options.transform = flip_y

    # (Test purposes)
    min_distance = math.sqrt((sender_body.position.x - receiver_body.position.x)**2 + (sender_body.position.y - receiver_body.position.y)**2)
    print(f"Distance between vehicles: {min_distance:.2f} meters")

    # Since .step accepts seconds, each step s 1/60th of a second, meaning the checking for collision goes on for 5 seconds (300/60)
    for _ in range(300):
        # NOTE: The drawing of the simulation is done in the pygame window
        draw(space, draw_options)

        if collision_time is not None:
            collision_detected = True
            # break
            sender_shape.color = (0, 0, 0, 255)
            receiver_shape.color = (0, 0, 0, 255)
        
        space.step(dt) # Step the physics simulation
        time_elapsed += dt

    export_final_frame() # The final frame is extracted from the window after the simulation is done and exported to the video_stream
    restore_background() # The window is restored with previous background stitched map before restarting the simulation and drawing of new frame

    #lowest_id = min(sender_id, receiver_id)
    # DUMMY ID for now
    lowest_id = 22

    time_overall = time.time() - time_overall  # Calculate time taken for the entire process
    print(f"Time taken for collision check: {time_overall:.2f} seconds")

    return collision_detected, lowest_id