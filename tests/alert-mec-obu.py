# This test script should create a websocket connection to ditto to receive collision alert messages
from websocket import WebSocketApp
import json
import base64
import time

def on_open(ws):
    print("[Ditto WS] Connection opened.")

    #ws.send(f"START-SEND-EVENTS?filter=and(eq(thingId,'{ditto_thing_id}'),or(eq(resource:path,'/features/Awareness'),eq(resource:path,'/features/Dynamics')))")
    ws.send("START-SEND-MESSAGES")

def on_message(ws, message):
    msg = json.loads(message)

    value = msg.get("value", {})

    t_rcv_obu = int(time.time() * 1000)  # Current time in milliseconds
    t_gen_mec = value.get("t_gen_mec", 0)
    delay = t_rcv_obu - t_gen_mec
    print(f"Latency from MEC to OBU (collision alerts): {delay} ms")

def on_error(ws, error):
    print("[Ditto WS] Websocket error:", error)

def on_close(ws, close_status_code, close_msg):
    print("[Ditto WS] Connection closed.")

def start_ditto_ws_listener():
    auth = "ditto:ditto"
    b64_auth = base64.b64encode(auth.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth}"
    }

    ws = WebSocketApp(
        "ws://10.255.41.5:8080/ws/2",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        header=headers
    )

    # Run in background
    ws.run_forever()