# This test script should create a websocket connection to ditto to receive collision alert messages

# TODO: Box Plots and CDFs of latencies
from websocket import WebSocketApp
import json
import base64
import time
import sys
import pandas as pd

LATENCY_LOG = "results/obu-alert-reception-times.csv"
MAX_SAMPLES = 6020

sample_count = 0

reception_times = []

def on_open(ws):
    print("[Ditto WS] Connection opened.")

    ws.send("START-SEND-MESSAGES")

def on_message(ws, message):
    global writer, logfile, sample_count, reception_times#delays
    try:
        msg = json.loads(message)
    except json.JSONDecodeError:
        #print("Received non-JSON message:", message)
        return

    t_alert_reception = time.time()
    reception_times.append(t_alert_reception)

    # Uncomment to calculate latency from MEC to OBU (receiving the alert)
        # raw_value = msg.get("value", {})
        # if isinstance(raw_value, str):
        #     try:
        #         value = json.loads(raw_value)
        #     except json.JSONDecodeError:
        #         print("Received non-JSON value:", raw_value)
        #         return
        # else:
        #     value = raw_value

        # t_rcv_obu = int(time.time() * 1000)  # Current time in milliseconds
        # t_gen_mec = value.get("t_gen_mec", 0)

        # if t_gen_mec:
        #     delay = t_rcv_obu - t_gen_mec
        #     print(f"Latency from MEC to OBU (collision alerts): {delay} ms")
            
        #     delays.append(delay)

    sample_count += 1
    if sample_count >= MAX_SAMPLES:
        pd.DataFrame(reception_times, columns=["reception_time"]).to_csv(LATENCY_LOG, index=False)
        print(f"Collected {MAX_SAMPLES} samples. Stopping listener.")
        ws.close()
        sys.exit(0)


def on_error(ws, error):
    print("[Ditto WS] Websocket error:", error)

def on_close(ws, close_status_code, close_msg):
    print("[Ditto WS] Connection closed.")

def start_alert_listener():
    auth = "ditto:ditto"
    b64_auth = base64.b64encode(auth.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth}"
    }

    ws = WebSocketApp(
        "ws://10.255.41.6:8080/ws/2",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        header=headers
    )

    # Run in background
    ws.run_forever()

if __name__ == "__main__":
    start_alert_listener()
