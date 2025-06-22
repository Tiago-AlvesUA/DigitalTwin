# This script should create a websocket connection to ditto to receive info from it and save it

# DITTO WS Listener for features/events/...

from config import DITTO_USERNAME, DITTO_PASSWORD, DITTO_WS_URL
from websocket import WebSocketApp
import json
import base64
import threading

#TODO: Use threading lock here
latest_awareness = None
latest_dynamics = None
data_lock = threading.Lock()


def get_awareness():
    with data_lock:
        return latest_awareness

def get_dynamics():
    with data_lock:
        return latest_dynamics

# https://eclipse.dev/ditto/basic-changenotifications.html
#   |
#   V
# https://eclipse.dev/ditto/basic-rql.html
# https://eclipse.dev/ditto/httpapi-protocol-bindings-websocket.html
def on_open(ws):
    print("[Ditto WS] Connection opened.")

    # START-SEND-EVENTS: Subscribe for Thing events/change notifications
    # RQL expressions to filter subscription notifications    
    #ws.send("START-SEND-EVENTS?filter=eq(resource:path,'/features/Awareness')")
    ws.send("START-SEND-EVENTS?filter=and(eq(thingId,'org.acme:my-device-2'),or(eq(resource:path,'/features/Awareness'),eq(resource:path,'/features/Dynamics')))")

    #print("[Ditto WS] Sent subscription commands.")

def on_message(ws, message):
    try:
        data = json.loads(message)

        if not data.get("value"):
            return
        
        feature_path = data.get("path", "")
        value = data.get("value")

        global latest_awareness, latest_dynamics
        with data_lock:
            if "features/Awareness" in feature_path:
                #print("[Ditto WS] Awareness Event received:")
                latest_awareness = value
            elif "features/Dynamics" in feature_path:
                #print("[Ditto WS] Dynamics Event received:")
                latest_dynamics = value
    except json.JSONDecodeError:
        print("[Ditto WS] Received non-JSON message:")
        #print(message)


def on_error(ws, error):
    print("[Ditto WS] Websocket error:", error)

def on_close(ws, close_status_code, close_msg):
    print("[Ditto WS] Connection closed.")

def start_ditto_ws_listener():
    auth = f"{DITTO_USERNAME}:{DITTO_PASSWORD}"
    b64_auth = base64.b64encode(auth.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth}"
    }

    ws = WebSocketApp(
        DITTO_WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        header=headers
    )

    # Run in background
    ws.run_forever()