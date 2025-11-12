from websocket import WebSocketApp
import json
import base64
import threading
import time

ws = None
speed = 90
max_samples = 10000
sample = 0

def send_speed_alert():
    global sample
    i=0
    while True:
        if ws is not None:
            if i < 5:
                # WITH COMMANDS
                advised_speed = speed - 10

                message = {
                    "topic": "org.acme/vehicle-1/things/twin/commands/modify",
                    #"topic": "org.acme/vehicle-1/things/live/messages/speed",
                    "headers": {},
                    "path": "/features/Speed/properties",
                    #"path": "/inbox/messages/speed",
                    "value": {
                        "collision": True,
                        "advisedSpeed": advised_speed
                    }
                }
                ws.send(json.dumps(message))
                print("[Ditto WS] Speed alert sent.")

                i += 1
                time.sleep(1)
            else:
                # WITH MESSAGES
                advised_speed = speed

                # https://eclipse.dev/hono/docs/user-guide/mqtt-adapter/
                
                # If response required is true, Ditto will include a request ID in the topic:
                # command/[${tenant-id}]/[${device-id}]/req/${req-id}/${command}
                # If false, there will be no request ID in the topic:
                # command/[${tenant-id}]/[${device-id}]/req//${command}

                # If the device needs to send a command response, the topic should be:
                # command/${tenant-id}/${device-id}/res/${req-id}/${status}
                message = {
                    "topic": "org.acme/vehicle-1/things/live/messages/speed",
                    "headers": {
                        "content-type": "text/plain",
                        #"correlation-id": "no-collision",
                        "response-required": "false"
                    },
                    #"path": "/features/Speed/properties",
                    "path": "/inbox/messages/speed",
                    "value": {
                        "collision": False,
                        "advisedSpeed": advised_speed
                    }
                }
                ws.send(json.dumps(message))
                #print("[Ditto WS] Chill Speed alert sent.")
            
                i = 0
                time.sleep(1)

            sample += 1
            if sample >= max_samples:
                print("[Ditto WS] Reached max samples. Stopping.")
                break

def on_open(ws_instance):
    print("[Ditto WS] Connection open for sending speed alerts.")
    threading.Thread(target=send_speed_alert, daemon=True).start()

def on_error(ws_instance, error):
    print("[Ditto WS] WebSocket error:", error)

def on_close(ws_instance, close_status_code, close_msg):
    print("[Ditto WS] Connection closed:", close_msg)

def start_sender_ws_listener():
    global ws

    auth = "ditto:ditto"
    b64_auth = base64.b64encode(auth.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth}"
    }
    # TODO: Alterei o link
    ws = WebSocketApp(
        "ws://10.255.41.6:8080/ws/2",
        on_open=on_open,
        on_error=on_error,
        on_close=on_close,
        header=headers
    )

    ws.run_forever()

if __name__ == "__main__":
    start_sender_ws_listener()
