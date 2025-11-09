import pygame
import math
import io
import requests
import numpy as np
from PIL import Image
from pyquadkey2 import quadkey
from utils.background_manager import stitch_tiles, remove_tiles_from_cache
from utils.tiles import It2s_Tiles
from messages.cam import delta_path_history_to_coordinates
from workers.ditto_listener import get_awareness
from config import STREAM_APP

# Initialize pygame and set up global surfaces
pygame.init()

WIDTH, HEIGHT = 768, 768
window = pygame.Surface((WIDTH, HEIGHT))
background_surface = pygame.Surface((WIDTH, HEIGHT))

# Global state for tile management
tile_x, tile_y, zoom = 0, 0, 17
current_qk = None  # Current quadkey being processed (center tile of pygame background)
current_grid = []  # Set to hold the current grid of tiles (for pygame background)


def position_of_vehicle(pixel_x, pixel_y):
    global tile_x, tile_y

    x = int(pixel_x - ((tile_x-1) * 256) - WIDTH // 2) # Adjust for tile offset and center the vehicle
    y = int(-1 * (pixel_y - ((tile_y-1) * 256) - HEIGHT // 2)) # Adjust for tile offset and center the vehicle

    return (x,y)


def latlon_to_img_pixel(lat, lon, zoom=17):
    """
    Convert latitude and longitude to pixel coordinates for a given tile at a certain zoom level.
    First, it converts latitude and longitude to Mercator projection coordinates,
    then it calculates the pixel coordinates based on the zoom level.
    """
    # Provides precise pixel coordinates in the correct tile
    lat_rad = math.radians(lat)
    x = math.floor((lon + 180.0) / 360.0 * (2.0 ** zoom) * 256)
    y = math.floor((1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) * 2.0 ** (zoom - 1) * 256)

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


def export_final_frame():
    data = pygame.surfarray.array3d(window)
    image = Image.fromarray(np.transpose(data, (1, 0, 2)))
    buf = io.BytesIO()
    image.save(buf, format='JPEG')
    buf.seek(0)

    requests.post(STREAM_APP, data=buf.getvalue(), headers={"Content-Type": "image/jpeg"})


def get_window_surface():
    return window


def restore_background():
    window.blit(background_surface,(0,0))


def get_window_dimensions():
    return WIDTH, HEIGHT


def create_collision_visualizer(current_dynamics, receiver_lat, receiver_lon, sender_id, sender_lat, sender_lon):    
    receiver_quadkey = quadkey.from_geo((receiver_lat/1e7,receiver_lon/1e7),17)
    draw_background(receiver_quadkey)

    # Obtain path history of the receiver vehicle from Digital Twin Dynamics feature
    if "lowFrequencyContainer" in current_dynamics["properties"]:
        receiver_delta_path_history = current_dynamics["properties"]["lowFrequencyContainer"]["pathHistory"]
        receiver_path_history = delta_path_history_to_coordinates(receiver_delta_path_history, (receiver_lat, receiver_lon))
        draw_path_history("receiver", receiver_path_history, (receiver_lat/1e7, receiver_lon/1e7))
    
    # Obtain path history of the sender vehicle from Digital Twin Awareness feature
    current_awareness = get_awareness()
    # NOTE: By the time the MCM was received there might not be current awareness yet (CAMs from other vehicles might not have been processed yet)
    if (current_awareness != None) and (str(sender_id) in current_awareness["properties"]):
        sender_delta_path_history = current_awareness["properties"][str(sender_id)]["pathHistory"]
        # sender_lat and sender_lon are provided in the MCM message
        sender_path_history = delta_path_history_to_coordinates(sender_delta_path_history, (sender_lat, sender_lon))
        draw_path_history("sender", sender_path_history, (receiver_lat/1e7, receiver_lon/1e7))