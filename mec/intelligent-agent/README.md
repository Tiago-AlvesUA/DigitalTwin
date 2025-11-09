## Configuration of the Agent

Before running the agent, a virtual environment must be created and the packages from requirements.txt must be installed via pip.
The package pyquadkey2 requires Python C headers to be installed as it is a small C extension. 
Consequently, the following three commands are necessary to setup the agent: 

`sudo apt install -y python3.10-dev build-essential`
`python3 -m venv venv`
`pip install -r requirements.txt`

## How to run

The first thing to run is `mjpeg_stream.py`. This is actually a different component from the Agent, but it is necessary so the Agent can send the visualizer frames so the video stream is created;
Secondly, run the `agent.py`. It starts three essential processes (mqtt_listener, ditto_listener, and ditto_sender).

## Agent structure

![alt text](agent_arch.png)

The agent is composed of 4 workers:
- **mqtt_listener(mqtt.py):** processes C-ITS messages from the es-broker and creates JSON messages to update Awareness, Dynamics, Perception, and Trajectories features in the Digital Twin. Also checks for potential future trajectory collisions: every time a MCM from other vehicle (sender) is received, a physics simulation is performed (`pymunk`) using the information from this message and also from local dynamics, which is the own vehicle (receiver) data;

- **ditto_listener:** listens for Dynamics and Awareness features update notifications, and stores their latest values (using a WebSocket connection to Ditto). Local dynamics is used for the collision checking process, while local awareness to draw path history in the visualizer;

- **ditto_sender:** sends the feature updates to Ditto via WebSocket connection;

- **visualizer:** draws a pygame visualization of the collision checking process.

### Links used

ditto_listener:
    https://eclipse.dev/ditto/basic-changenotifications.html
    https://eclipse.dev/ditto/basic-rql.html
    https://eclipse.dev/ditto/httpapi-protocol-bindings-websocket.html

visualizer:
    https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames (latlon_to_img_pixel())