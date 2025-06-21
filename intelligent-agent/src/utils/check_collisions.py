import math
# import json
import requests
# from dataclasses import dataclass
from utils.ditto import get_dynamics, get_awareness
from workers.shared_memory import messages
from messages.cam import delta_path_history_to_coordinates
from utils.tile_manager import stitch_tiles, remove_tiles_from_cache
from utils.tiles import It2s_Tiles
import utm
import pymunk
import pymunk.pygame_util
import pygame
from PIL import Image
import numpy as np
import io
from pyquadkey2 import quadkey
from io import BytesIO
import mercantile
import time

pygame.init()

time_elapsed = 0.0
collision_time = None
WIDTH, HEIGHT = 768, 768 # For testing purposes, use a smaller window
window = pygame.Surface((WIDTH, HEIGHT))
background_surface = pygame.Surface((WIDTH, HEIGHT))    # To hold the background image
tile_x, tile_y, zoom = 0, 0, 17  # Default values for tile coordinates and zoom level
#necessary
current_qk = None  # Current quadkey being processed (center tile of pygame background)
#necessary
current_grid = []  # Set to hold the current grid of tiles (for pygame background)


def compass_to_trigonometric_angle(degrees_heading):
    return math.radians(90 - degrees_heading)

def apply_force(vehicle, acceleration):
    force = vehicle.mass * acceleration # F = m * a (Newton's second law)
    heading = vehicle.angle

    force_x = force * math.cos(heading)
    force_y = force * math.sin(heading)

    vehicle.apply_force_at_local_point((force_x,force_y), (0,0))    # Always applied at position (0,0) since it is the Center of Mass of the object (it already takes in consideration the coordinates where the object is)

# https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
def latlon_to_img_pixel(lat, lon, zoom=17):
    """
    Convert latitude and longitude to pixel coordinates for a given tile at a certain zoom level.
    First, it converts latitude and longitude to Mercator projection coordinates,
    then it calculates the pixel coordinates based on the zoom level.
    """

    lat_rad = math.radians(lat)
    x = math.floor((lon + 180.0) / 360.0 * (2.0 ** zoom) * 256)
    y = math.floor((1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) * 2.0 ** (zoom - 1) * 256)
    # print(f"Pixel coordinates: ({x}, {y})")
    return (x, y)



def draw_background(qk):
    global ref_coord, tile_x, tile_y, zoom, current_qk, current_grid

    #qk = quadkey.from_str(qk)  
    tile_original = qk.to_tile()
    tile_x, tile_y, zoom = tile_original[0][0], tile_original[0][1], tile_original[1]

    qk_str = str(qk)  # Convert quadkey to string representation
    qk_str = '/'.join(qk_str) 


    if qk_str == current_qk:    # If the quadkey did not change, do not redraw the background
        return
    else:
        current_qk = qk_str

    it2s_tiles = It2s_Tiles()
    # Get all the adjacent tiles/quadkeys
    adjacent_quadkeys = it2s_tiles.it2s_get_all_adjacent_tiles(qk_str)

    # This new grid is composed of 9 tiles (1 center tile and 8 adjacent tiles)
    new_grid = []

    for tile in adjacent_quadkeys:
        new_grid.append(tile)

    tiles_to_remove = [tile for tile in current_grid if tile not in new_grid]
    if tiles_to_remove:
        remove_tiles_from_cache(tiles_to_remove)

    current_grid = new_grid  # Update the current tiles set

    # NOTE: All information regarding the tiles should be stored in arrays, in order to have ordered access to them
    stitched_empty = Image.new("RGB", (768, 768))  # Create a new image to stitch the tiles
    
    stitched = stitch_tiles(stitched_empty, new_grid)  # Stitch the tiles together

    mode = stitched.mode
    size = stitched.size
    data = stitched.tobytes()
    
    # Create Pygame surface
    if mode == "RGB":
        pygame_image = pygame.image.fromstring(data, size, "RGB")
    elif mode == "RGBA":
        pygame_image = pygame.image.fromstring(data, size, "RGBA")
    else:
        # Convert to RGB if unexpected mode
        stitched = stitched.convert("RGB")
        pygame_image = pygame.image.fromstring(stitched.tobytes(), stitched.size, "RGB")
    
    pygame_image = pygame.transform.scale(pygame_image, (WIDTH, HEIGHT))
    window.blit(pygame_image, (0, 0))
    background_surface.blit(pygame_image, (0, 0))  # Store the background image for later use


def draw_path_history(vehicle_type, path_history, ref_coord):
    global window, tile_x, tile_y, zoom

    #print(f"Path history: {path_history}")

    if vehicle_type == "sender":
        color = (0, 0, 255, 255) # Blue
    elif vehicle_type == "receiver":
        color = (255, 0, 0, 255) # Red
    else:
        return
    
    # Transform each coordinate in the path history to UTM
    for point in path_history:
        #print(f"Point: {point}")
        point_position = latlon_to_img_pixel(point[0],point[1])#coordinates_to_utm(point)#,ref_coord)
        # Apply same transform as draw_options.transform (flip Y and translate to center)
        screen_x = int(point_position[0] - (tile_x-1) * 256)
        screen_y = int(point_position[1] - (tile_y-1) * 256)

        # Check bounds to avoid crashing or drawing off-screen
        if 0 <= screen_x < WIDTH and 0 <= screen_y < HEIGHT:
            pygame.draw.circle(window, color, (screen_x, screen_y), 4)


def create_vehicle(space, position, mass, width, length, heading, speed, color):
    global tile_x, tile_y, zoom
    # Since pymunk does not care about length, it just draws a rectangle where width is aligned with the x-axis and height with the y-axis, we need to switch width and length
    box_width = length
    box_height = width
    body = pymunk.Body(mass, pymunk.moment_for_box(mass, (box_width, box_height))) # Moment for box calculates moment of intertia, which is necessary to determine resistance to rotational motion (and behave more realistically)

    x = int(position[0] - ((tile_x-1) * 256) - WIDTH // 2)  # Adjust for tile offset and center the vehicle
    y = int(-1 * (position[1] - ((tile_y-1) * 256) - HEIGHT // 2))  # Adjust for tile offset and center the vehicle

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
    #print(f"Sender ID: {sender_id}")
    
    time_overall = time.time()  # Start timer for performance measurement

    time_elapsed = 0.0
    collision_time = None

    fps = 60
    dt = 1/fps

    space = pymunk.Space()
    space.gravity = (0,0)

    collision_detected = False
    #print(f"Sender LAT: {sender_lat}")
    #print(f"Sender LON: {sender_lon}")

    time_test = time.time()  # Start timer for performance measurement
    # First collect necessary data to calculate the receiver path
    current_dynamics = get_dynamics()
    #print(f"Current dynamics: {current_dynamics}")
    time_test = time.time() - time_test  # Calculate time taken for the entire process
    print(f"Time to get dynamics from ditto: {time_test:.2f} seconds")

    #### RECEIVER DATA #### TODO: No need to get ID from the vehicle since i already get it from the toml file (?)
    receiver_lat = current_dynamics["properties"]["basicContainer"]["referencePosition"]["latitude"]
    receiver_lon = current_dynamics["properties"]["basicContainer"]["referencePosition"]["longitude"]
    receiver_heading = current_dynamics["properties"]["highFrequencyContainer"]["heading"]["headingValue"]
    receiver_speed = current_dynamics["properties"]["highFrequencyContainer"]["speed"]["speedValue"]
    receiver_id = 21 # DUMMY, should get from toml file

    
    ##################### DRAW BACKGROUND MAP ###################
    receiver_quadkey = quadkey.from_geo((receiver_lat/1e7,receiver_lon/1e7),zoom)
    draw_background(receiver_quadkey)

    #############################################################




    #################### DRAW PATH HISTORY OF BOTH VEHICLES ###################
    # Obtaining path history from ditto, feature Dynamics (Dynamics is updated by the intelligent agent - mqtt.py that processes broker messages)
    if "lowFrequencyContainer" in current_dynamics["properties"]:
        receiver_delta_path_history = current_dynamics["properties"]["lowFrequencyContainer"]["pathHistory"]
        receiver_path_history = delta_path_history_to_coordinates(receiver_delta_path_history, (receiver_lat, receiver_lon))
        draw_path_history("receiver", receiver_path_history, (receiver_lat/1e7, receiver_lon/1e7))
    # Obtaining path history from ditto, feature Awareness (Awareness is updated by the intelligent agent - mqtt.py that processes broker messages)
    time_test = time.time()  # Start timer for performance measurement
    current_awareness = get_awareness()
    time_test = time.time() - time_test  # Calculate time taken for the entire process
    print(f"Time to get awareness from ditto: {time_test:.2f} seconds")

    # check if the sender_id exists in the awareness properties
    if str(sender_id) in current_awareness["properties"]:
        sender_delta_path_history = current_awareness["properties"][str(sender_id)]["pathHistory"]
        # Mistura, path history vou buscar ao ditto, mas sender_lat e lon vou buscar à MCM
        sender_path_history = delta_path_history_to_coordinates(sender_delta_path_history, (sender_lat, sender_lon))
        draw_path_history("sender", sender_path_history, (receiver_lat/1e7, receiver_lon/1e7))
    ############################################################################




    # Transform spherical coordinates into UTM ones (plane).TODO TODO: Must get reference position from the receiver to serve as normalizer
    sender_position = latlon_to_img_pixel(sender_lat/1e7,sender_lon/1e7)#coordinates_to_utm((sender_lat/1e7, sender_lon/1e7))#, (receiver_lat/1e7, receiver_lon/1e7))
    receiver_position = latlon_to_img_pixel(receiver_lat/1e7,receiver_lon/1e7)#coordinates_to_utm((receiver_lat/1e7, receiver_lon/1e7))#, (receiver_lat/1e7, receiver_lon/1e7))
   
    # Heading comes in compass degrees, so we need to convert it to a trigonometric angle
    sender_heading = compass_to_trigonometric_angle(sender_heading/10)
    receiver_heading = compass_to_trigonometric_angle(receiver_heading/10)


    sender_body, sender_shape = create_vehicle(space, sender_position, 10, 1.8, 4.3, sender_heading, sender_speed*1e-2, color=(0, 0, 255, 255)) # blue
    receiver_body, receiver_shape = create_vehicle(space, receiver_position, 10, 1.8, 4.3, receiver_heading, receiver_speed*1e-2, color=(255, 0, 0, 255)) # red

    collision = space.add_collision_handler(1,1)  # Type 1 = Cars
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
            # collision_detected = True
            # break
            # Change vehicle trajectory colors to white
            sender_shape.color = (0, 0, 0, 255)
            receiver_shape.color = (0, 0, 0, 255)
        
        space.step(dt) # Step the physics simulation
        time_elapsed += dt

    data = pygame.surfarray.array3d(window)
    image = Image.fromarray(np.transpose(data, (1, 0, 2)))
    buf = io.BytesIO()
    image.save(buf, format='JPEG')

    buf.seek(0)
    
    response = requests.post("http://localhost:5000/", data=buf.getvalue(), headers={"Content-Type": "image/jpeg"})

    #window.fill((0, 0, 0)) # Reset window after sending the frame (Reset between each simulation)
    window.blit(background_surface, (0, 0))  # Restore the background image

    print(f"Distance between vehicles: {min_distance:.2f} meters")

    lowest_id = min(sender_id, receiver_id)

    time_overall = time.time() - time_overall  # Calculate time taken for the entire process
    print(f"Time taken for collision check: {time_overall:.2f} seconds")

    return collision_detected, lowest_id