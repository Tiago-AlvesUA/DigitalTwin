from pygeotile.tile import Tile
import requests

DITTO_BASE_URL = "http://10.255.41.221:8080/api/2/things"
DITTO_THING_ID = "org.acme:my-device-2"
DITTO_USERNAME = 'ditto'
DITTO_PASSWORD = 'ditto'

def get_ditto_coordinates():
    url = f"{DITTO_BASE_URL}/{DITTO_THING_ID}/features/localTwin"

    response = requests.get(url, auth=(DITTO_USERNAME, DITTO_PASSWORD))

    if response.status_code == 200:
        feature_properties = response.json()
        print(response.json())
    else:
        print(f"Failed to get Ditto twin. Status code: {response.status_code}")
        print("Response:", response.text)
    
    latitude = feature_properties["properties"]["referencePosition"]["properties"]["latitude"]/10**7
    longitude = feature_properties["properties"]["referencePosition"]["properties"]["longitude"]/10**7

    print (latitude, longitude)

    return latitude, longitude

def get_quadtree():
    latitude, longitude = get_ditto_coordinates()

    # create tile with zoom level of 14
    tile = Tile.for_latitude_longitude(latitude, longitude, 14)
    print(tile)

    tms = tile.tms
    print(tms)

    # convert to quadtree
    quadtree = tile.quad_tree
    print(quadtree)

    # tile = Tile.for_latitude_longitude(latitude, longitude, 12)
    # print(tile)
    # quadtree = tile.quad_tree
    # print(quadtree)


if __name__ == "__main__":
    get_quadtree()