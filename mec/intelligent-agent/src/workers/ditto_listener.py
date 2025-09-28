# This script should create a websocket connection to ditto to receive info from it and save it

# DITTO WS Listener for features/events/...

from config import DITTO_USERNAME, DITTO_PASSWORD, DITTO_WS_URL, DITTO_THING_NAMESPACE, DITTO_THING_NAME
from websocket import WebSocketApp
import json
import base64
import threading
import time

latest_awareness = None
latest_dynamics = None
data_lock = threading.Lock()

def current_milli_time():
    return (round(time.time() * 1000) + 5000) - 1072915200000

# Own car
def get_dynamics():
    with data_lock:
        return latest_dynamics
    
# Other vehicles
def get_awareness():
    with data_lock:
        return latest_awareness

# https://eclipse.dev/ditto/basic-changenotifications.html
# https://eclipse.dev/ditto/basic-rql.html
# https://eclipse.dev/ditto/httpapi-protocol-bindings-websocket.html
def on_open(ws):
    print("[Ditto WS] Connection opened.")

    ditto_thing_id = f"{DITTO_THING_NAMESPACE}:{DITTO_THING_NAME}"
    # START-SEND-EVENTS: Subscribe for Thing events/change notifications
    # RQL expressions to filter subscription notifications    
    ws.send(f"START-SEND-EVENTS?filter=and(eq(thingId,'{ditto_thing_id}'),or(eq(resource:path,'/features/Awareness'),eq(resource:path,'/features/Dynamics')))")
    #ws.send("START-SEND-MESSAGES")

    #print("[Ditto WS] Sent subscription commands.")

def on_message(ws, message):
    try:
        data = json.loads(message)

        if not data.get("value"):
            return
        
        path = data.get("path", "")
        value = data.get("value")

        global latest_awareness, latest_dynamics
        with data_lock:
            if "features/Awareness" in path:
                # TODO: Time it took to receive the event
                # TODO: Subtract generation delta time of the message (CAM) to get real latency

                latest_awareness = value
            
                # # Get the delay the message took to be processed into a feature and received as an event
                # t_awareness_rcv_mec = current_milli_time() % 65536  # Current time in milliseconds
                # t_cam_gen_obu = value.get("properties",{}).get("generationDeltaTime", 0)

                # if t_cam_gen_obu:
                #     if t_awareness_rcv_mec > t_cam_gen_obu:
                #         delay = t_awareness_rcv_mec - t_cam_gen_obu
                #     elif t_awareness_rcv_mec < t_cam_gen_obu:
                #         delay = t_awareness_rcv_mec + 65536 - t_cam_gen_obu
                #     else:
                #         delay = 0

                #     print(f"Network delay from OBU to MEC (Process into feature and retrieved at the Agent): {delay} ms")

            # Own car data (CAMs)
            elif "features/Dynamics" in path:
                latest_dynamics = value

                # # Get the delay the message took to be processed into a feature and received as an event
                # t_awareness_rcv_mec = current_milli_time() % 65536  # Current time in milliseconds
                # t_cam_gen_obu = value.get("properties",{}).get("generationDeltaTime", 0)

                # if t_cam_gen_obu:
                #     if t_awareness_rcv_mec > t_cam_gen_obu:
                #         delay = t_awareness_rcv_mec - t_cam_gen_obu
                #     elif t_awareness_rcv_mec < t_cam_gen_obu:
                #         delay = t_awareness_rcv_mec + 65536 - t_cam_gen_obu
                #     else:
                #         delay = 0

                #     #print(f"Network delay from OBU to MEC (Process into feature and retrieved at the Agent): {delay} ms")

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