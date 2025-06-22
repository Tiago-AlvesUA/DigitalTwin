from config import DITTO_USERNAME, DITTO_PASSWORD, DITTO_WS_URL
from websocket import WebSocketApp
import json
import base64

ws = None

def update_ditto_awareness(awareness):
    global ws

    if ws == None:
        return
    else:
        message = {
            "topic": "org.acme/my-device-2/things/twin/commands/modify",
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
            "topic": "org.acme/my-device-2/things/twin/commands/modify",
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
            "topic": "org.acme/my-device-2/things/twin/commands/modify",
            "headers": {},
            "path": "/features/Dynamics",
            "value": dynamics
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
