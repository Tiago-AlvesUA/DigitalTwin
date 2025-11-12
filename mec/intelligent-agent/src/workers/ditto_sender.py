from config import DITTO_USERNAME, DITTO_PASSWORD, DITTO_WS_URL, DITTO_THING_NAMESPACE, DITTO_THING_NAME
from websocket import WebSocketApp
import json
import base64
import time

ws = None

def update_ditto_awareness(awareness):
    global ws

    if ws == None:
        return
    else:
        message = {
            "topic": f"{DITTO_THING_NAMESPACE}/{DITTO_THING_NAME}/things/twin/commands/modify",
            "headers": {},
            "path": "/features/Awareness",
            "value": awareness
        }
        ws.send(json.dumps(message))

def update_ditto_perception(perception):
    global ws

    if ws == None:
        return
    else:
        message = {
            "topic": f"{DITTO_THING_NAMESPACE}/{DITTO_THING_NAME}/things/twin/commands/modify",
            "headers": {},
            "path": "/features/Perception",
            "value": perception
        }
        ws.send(json.dumps(message))


def update_ditto_dynamics(dynamics):
    global ws

    if ws == None:
        return
    else:
        message = {
            "topic": f"{DITTO_THING_NAMESPACE}/{DITTO_THING_NAME}/things/twin/commands/modify",
            "headers": {},
            "path": "/features/Dynamics",
            "value": dynamics
        }
        ws.send(json.dumps(message))

def update_ditto_trajectories(trajectories):
    global ws

    if ws == None:
        return
    else:
        message = {
            "topic": f"{DITTO_THING_NAMESPACE}/{DITTO_THING_NAME}/things/twin/commands/modify",
            "headers": {},
            "path": "/features/Trajectories",
            "value": trajectories
        }
        ws.send(json.dumps(message))

def update_vehicle_speed(exists_collision, receiver_speed, avoidanceSpeedReduction):
    global ws

    if ws == None:
        return

    t_gen_mec = int(time.time() * 1000)  # Current time in milliseconds

    if exists_collision:
        # If exists a collision, reduce speed for below the limit
        receiver_speed_kmh = receiver_speed * 0.036  # Convert m/s to km/h
        advised_speed = receiver_speed_kmh - avoidanceSpeedReduction

        message = {
            "topic": f"{DITTO_THING_NAMESPACE}/{DITTO_THING_NAME}/things/live/messages/speed",
            "headers": {
                "content-type": "text/plain",
                #"correlation-id": "reducing-speed"
                "response-required": "false"
            },
            "path": "/inbox/messages/speed",
            "value": {
                "t_gen_mec": t_gen_mec,
                "collision": True,
                "advisedSpeed": advised_speed
            }
        }
    else:
        # If no collision, keep current speed
        advised_speed = receiver_speed * 0.036  # Convert m/s to km/h
        message = {
            "topic": f"{DITTO_THING_NAMESPACE}/{DITTO_THING_NAME}/things/live/messages/speed",
            "headers": {
                "content-type": "text/plain",
                #"correlation-id": "no-collision"
                "response-required": "false"
            },
            "path": "/inbox/messages/speed",
            "value": {
                "t_gen_mec": t_gen_mec,
                "collision": False,
                "advisedSpeed": advised_speed
            }
        }
    
    ws.send(json.dumps(message))


def on_open(ws):
    print("[Ditto WS] Connection open for sending telemetry.")

def on_error(ws, error):
    print("[Ditto WS] Websocket error:", error)

def on_close(ws, close_status_code, close_msg):
    print("[Ditto WS] Connection closed.")

def start_sender_ws_listener():
    global ws

    auth = f"{DITTO_USERNAME}:{DITTO_PASSWORD}"
    b64_auth = base64.b64encode(auth.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth}"
    }

    ws = WebSocketApp(
        DITTO_WS_URL,
        on_open=on_open,
        on_error=on_error,
        on_close=on_close,
        header=headers
    )

    # Run in background
    ws.run_forever()
