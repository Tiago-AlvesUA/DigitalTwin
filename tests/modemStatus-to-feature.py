# This test script obtains delays since the CAM was generated at the OBU until it is received at the MEC, processed into a feature and received as an event

# This test script should create a websocket connection to ditto to receive collision alert messages

# TODO: Box Plots and CDFs of latencies
from websocket import WebSocketApp
import json
import base64
import time
import csv
import sys

latency_log = "results/latencies-modemStatus-to-feature.csv"
MAX_SAMPLES = 1000

sample_count = 0

def current_milli_time():
    return (round(time.time() * 1000) + 5000) - 1072915200000

def on_open(ws):
    print("[Ditto WS] Connection opened.")

    ws.send(f"START-SEND-EVENTS?filter=and(eq(thingId,'org.acme:my-device-1'),eq(resource:path,'/features/ModemStatus/properties'))")

def on_message(ws, message):
    global writer, logfile, sample_count

    try:
        msg = json.loads(message)
    except json.JSONDecodeError:
        #print("Received non-JSON message:", message)
        return
    
    path = msg.get("path", "")
    value = msg.get("value")

    if "features/Awareness" in path:
        return
    
    # Own car data (CAMs)
    elif "features/ModemStatus" in path:

        # Get the delay the message took to be processed into a feature and received as an event
        t_awareness_rcv_mec_raw = current_milli_time() #% 65536  # Current time in milliseconds
        print(f"t_awareness_rcv_mec: {t_awareness_rcv_mec_raw}")
        t_awareness_rcv_mec = t_awareness_rcv_mec_raw % 65536  # Current time in milliseconds, modulo 65536 to match CAM reference time format
        #t_cam_gen_obu_raw = value.get("properties",{}).get("referenceTime", 0)
        t_cam_gen_obu_raw = value.get("referenceTime", 0)
        print(f"t_cam_gen_obu: {t_cam_gen_obu_raw}")
        t_cam_gen_obu = t_cam_gen_obu_raw % 65536  # Reference time from the CAM, in milliseconds

        if t_cam_gen_obu:
            if t_awareness_rcv_mec > t_cam_gen_obu:
                delay = t_awareness_rcv_mec - t_cam_gen_obu
            elif t_awareness_rcv_mec < t_cam_gen_obu:
                delay = t_awareness_rcv_mec + 65536 - t_cam_gen_obu
            else:
                delay = 0

            #print(f"Network delay from OBU to MEC (Process into feature and retrieved at the Agent): {delay} ms")
            writer.writerow([delay])
            logfile.flush()

            sample_count += 1
            if sample_count >= MAX_SAMPLES:
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
        "ws://10.255.41.5:8080/ws/2",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        header=headers
    )

    # Run in background
    ws.run_forever()

if __name__ == "__main__":
    with open(latency_log, mode='w', newline='') as logfile:
        global writer
        writer = csv.writer(logfile)
        writer.writerow(["Latency (ms)"])
        start_alert_listener()