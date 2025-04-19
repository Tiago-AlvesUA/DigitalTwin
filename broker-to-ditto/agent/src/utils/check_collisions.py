import math
import json
import requests
from dataclasses import dataclass
from config import DITTO_BASE_URL, DITTO_THING_ID, DITTO_USERNAME, DITTO_PASSWORD
from utils.ditto import get_dynamics
from workers.shared_memory import messages
import utm
import pymunk
import pymunk.pygame_util
import pygame
import os

time_elapsed = 0.0
collision_time = None
pygame.init()
WIDTH, HEIGHT = 500, 300
window = pygame.Surface((WIDTH, HEIGHT))

def compass_to_trigonometric_angle(degrees_heading):
    return math.radians(90 - degrees_heading)

def apply_force(vehicle, acceleration):
    force = vehicle.mass * acceleration # F = m * a (Newton's second law)
    heading = vehicle.angle

    force_x = force * math.cos(heading)
    force_y = force * math.sin(heading)

    #vehicle.apply_impulse_at_local_point((force_x,force_y), (0,0))
    vehicle.apply_force_at_local_point((force_x,force_y), (0,0))    # Always applied at position (0,0) since it is the Center of Mass of the object (it already takes in consideration the coordinates where the object is)

def coordinates_to_utm(coord):
    coordUTM = utm.from_latlon(*coord)

    # TODO: Change this normalization to be relative to the receiver position
    x = coordUTM[0] - 526186
    y = coordUTM[1] - 4497892

    return (x,y)

def create_vehicle(space, position, mass, width, length, heading, speed, color):
    # Since pymunk does not care about length, it just draws a rectangle where width is aligned with the x-axis and height with the y-axis, we need to switch width and length
    box_width = length
    box_height = width
    body = pymunk.Body(mass, pymunk.moment_for_box(mass, (box_width, box_height))) # Moment for box calculates moment of intertia, which is necessary to determine resistance to rotational motion (and behave more realistically)
    x, y = position
    body.position = (x,y)
    body.angle = heading
    # Using initial speed to calculate velocity
    velocity_x = speed * math.cos(heading)
    velocity_y = speed * math.sin(heading)
    body.velocity = (velocity_x, velocity_y)

    # pymunk.Poly is a convex polygon shape
    shape = pymunk.Poly.create_box(body, (width, length))
    shape.mass = mass
    shape.collision_type = 1
    shape.color = pygame.Color(*color)

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
    global collision_time, time_elapsed, window
    print(f"Sender ID: {sender_id}")

    time_elapsed = 0.0
    collision_time = None

    fps = 60
    dt = 1/fps

    space = pymunk.Space()
    space.gravity = (0,0)

    collision_detected = False
    print(f"Sender LAT: {sender_lat}")
    print(f"Sender LON: {sender_lon}")

    # TODO: Check if can get the dynamics from ditto or if i have to obtain them from the data reader
    # First collect necessary data to calculate the receiver path
    ###current_dynamics = get_dynamics()
    
    #### RECEIVER DATA #### TODO: No need to get ID from the vehicle since i already get it from the toml file (?)
    ###receiver_lat = current_dynamics["properties"]["basicContainer"]["referencePosition"]["latitude"]
    ###receiver_lon = current_dynamics["properties"]["basicContainer"]["referencePosition"]["longitude"]
    ###receiver_heading = current_dynamics["properties"]["highFrequencyContainer"]["heading"]["headingValue"]
    ###receiver_speed = current_dynamics["properties"]["highFrequencyContainer"]["speed"]["speedValue"]
    receiver_id = 21 # DUMMY, should get from toml file

    # Transform spherical coordinates into UTM ones (plane). TODO: Must get reference position from the receiver to serve as normalizer
    sender_position = coordinates_to_utm((sender_lat/1e7, sender_lon/1e7))
    receiver_position = coordinates_to_utm((40.6318981, -8.6903491))
   
    # Heading comes in compass degrees, so we need to convert it to a trigonometric angle
    sender_heading = compass_to_trigonometric_angle(sender_heading/10)
    receiver_heading = compass_to_trigonometric_angle(2000/10)

    # TODO: Check how i should introduce speed for the simulated vehicle
    sender_body, sender_shape = create_vehicle(space, sender_position, 10, 1.8, 4.3, sender_heading, sender_speed*1e-2, color=(0, 0, 255, 255)) # blue
    receiver_body, receiver_shape = create_vehicle(space, receiver_position, 10, 1.8, 4.3, receiver_heading, 2500*1e-2, color=(255, 0, 0, 255)) # red

    collision = space.add_collision_handler(1, 1)  # Type 1 = Cars
    collision.begin = collision_handler

    draw_options = pymunk.pygame_util.DrawOptions(window)
    # Flip Y-axis, since pygame origin is at the top left corner
    # Also, translate the origin to the center of the screen
    flip_y = pymunk.Transform(a=1, b=0, c=0, d=-1, tx=WIDTH // 2, ty=HEIGHT // 2)
    draw_options.transform = flip_y

    min_distance = math.sqrt((sender_body.position.x - receiver_body.position.x)**2 + (sender_body.position.y - receiver_body.position.y)**2)

    # Since .step accepts seconds, each step s 1/60th of a second, meaning the checking for collision goes on for 5 seconds (300/60)
    for _ in range(300):
        draw(space, draw_options)

        if collision_time is not None:
            # Change color to white
            collision_detected = True
            break
            # sender_shape.color = (255, 255, 255, 255)
            # receiver_shape.color = (255, 255, 255, 255)
        
        space.step(dt) # Step the physics simulation
        time_elapsed += dt

    # output_dir = "simulation_frames"
    # os.makedirs(output_dir, exist_ok=True) # Create folder if it doesn't exist
    # image_path = os.path.join(output_dir, "final_frame.jpg") # Save the last frame in the folder
    # pygame.image.save(window, image_path)

    print(f"Distance between vehicles: {min_distance:.2f} meters")

    lowest_id = min(sender_id, receiver_id)

    return collision_detected, lowest_id