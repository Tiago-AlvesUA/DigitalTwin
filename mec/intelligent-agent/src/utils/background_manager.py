import requests
from PIL import Image
from io import BytesIO
from pyquadkey2 import quadkey  # Assuming you have a quadkey module for handling

tile_cache = {}  # Global cache for downloaded tiles

# Knowing it is a 768x768 grid of tiles,the possitions are done accordingly to the order of adjacent_tiles() from tiles.py
POSITIONS_PIXELS = [
        (512, 256),   (0, 256),   (256, 512),
        (256,0), (512,0), (512, 512), 
        (0,512), (0,0), (256, 256)
    ]

def download_tile(tile_x, tile_y, zoom):
    global tile_cache

    if (tile_x, tile_y, zoom) in tile_cache:
        return tile_cache[(tile_x, tile_y, zoom)]

    url = f"https://tile.openstreetmap.org/{zoom}/{tile_x}/{tile_y}.png"
    headers = {"User-Agent": "MyPygameMapApp/1.0 (tiagojba9@gmail.com)"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        tile = Image.open(BytesIO(response.content))
        tile_cache[(tile_x, tile_y, zoom)] = tile  # Cache the downloaded tile
        return tile
    else:
        print(f"Failed to download tile {tile_x},{tile_y} @ zoom {zoom}")
        return Image.new("RGB", (256, 256), (0, 0, 0))  # fallback blank tile

def stitch_tiles(stitched_img, new_quadkeys):
    for idx, qk_str in enumerate(new_quadkeys):
        simple_tile = qk_str.replace('/', '')
        tile_coordinates = quadkey.from_str(simple_tile).to_tile()
        x,y,z = tile_coordinates[0][0], tile_coordinates[0][1], tile_coordinates[1]  # tile x, tile y, zoom level
        tile_img = download_tile(x, y, z)
        grid_index = POSITIONS_PIXELS[idx]  # Get the position of the tile in the grid
        stitched_img.paste(tile_img, grid_index)  # Paste the tile image at the correct position
    return stitched_img

def remove_tiles_from_cache(tiles_to_remove):
    global tile_cache

    for tile in tiles_to_remove:
        simple_tile = tile.replace('/', '')  # Remove slashes for quadkey
        tile_coordinates = quadkey.from_str(simple_tile).to_tile()  # Convert to tile coordinates
        x, y, z = tile_coordinates[0][0], tile_coordinates[0][1], tile_coordinates[1]  # tile x, tile y, zoom level
        if (x,y,z) in tile_cache:
            del tile_cache[(x, y, z)] # Remove tile from cache