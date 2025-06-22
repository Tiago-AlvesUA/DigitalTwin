from config import DITTO_BASE_URL, DITTO_THING_ID, DITTO_USERNAME, DITTO_PASSWORD
import requests
import time
#import global_vars


def update_ditto_trajectories(trajectories):
    url = f"{DITTO_BASE_URL}/{DITTO_THING_ID}/features/Trajectories"
    # Set up headers and basic authentication
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    requests.put(url, headers=headers, auth=(DITTO_USERNAME, DITTO_PASSWORD), json=trajectories)
    # global_vars.last_local_trajectories_update = time.time()

def update_ditto_perception(perception):
    url = f"{DITTO_BASE_URL}/{DITTO_THING_ID}/features/Perception"
    # Set up headers and basic authentication
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    
    # Send HTTP PUT request to update the twin in Ditto; TODO: Verify status code of response if needed
    #TODO: uncomment (ditto url not working)
    requests.put(url, headers=headers, auth=(DITTO_USERNAME, DITTO_PASSWORD), json=perception)
    # global_vars.last_local_perception_update = time.time()


def update_ditto_awareness(awareness):
    url = f"{DITTO_BASE_URL}/{DITTO_THING_ID}/features/Awareness"
    # Set up headers and basic authentication
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    
    # Send HTTP PUT request to update the twin in Ditto; TODO: Verify status code of response if needed
    #TODO: uncomment (ditto url not working)
    requests.put(url, headers=headers, auth=(DITTO_USERNAME, DITTO_PASSWORD), json=awareness)
    # global_vars.last_local_awareness_update = time.time()


# def update_ditto_dynamics(dynamics):


# def update_ditto_dynamics(dynamics):
#     url = f"{DITTO_BASE_URL}/{DITTO_THING_ID}/features/Dynamics"
#     # Set up headers and basic authentication
#     headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    
#     # Send HTTP PUT request to update the twin in Ditto; TODO: Verify status code of response if needed
#     #TODO: uncomment (ditto url not working)
#     response = requests.put(url, headers=headers, auth=(DITTO_USERNAME, DITTO_PASSWORD), json=dynamics)
#     # if response.status_code in (201, 204):
#     #     print("Ditto twin updated successfully.")
#     # else:
#     #     print(f"Failed to update twin. Status code; {response.status_code}")
#     #     print("Response: ", response.text)

def update_speed(data, thing_id):
    url = f"{DITTO_BASE_URL}/{thing_id}/inbox/messages/UpdateSpeed"
    print(f" URL: {url}")
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    payload = {
        "speed": data
    }
    response = requests.post(url, headers=headers, auth=(DITTO_USERNAME, DITTO_PASSWORD), json=payload)
    if response.status_code == 200:
        print("Speed updated successfully.")
    else:
        print(f"Failed to update speed. Status code: {response.status_code}")
        print("Response: ", response.text)

def get_dynamics():
    url = f"{DITTO_BASE_URL}/{DITTO_THING_ID}/features/Dynamics"
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = requests.get(url, headers=headers, auth=(DITTO_USERNAME, DITTO_PASSWORD))
    dynamics = response.json()
    return dynamics

def get_awareness():
    url = f"{DITTO_BASE_URL}/{DITTO_THING_ID}/features/Awareness"
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = requests.get(url, headers=headers, auth=(DITTO_USERNAME, DITTO_PASSWORD))
    awareness = response.json()
    return awareness