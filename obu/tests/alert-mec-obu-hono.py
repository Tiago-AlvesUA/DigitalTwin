import paho.mqtt.client as mqtt
import json

BROKER = "10.255.41.6"      # or your Hono adapter host
PORT = 8883
TENANT = "my-tenant"
DEVICE_ID = "org.acme:vehicle-1"      # as registered in Hono
USERNAME = "auth-id-1@my-tenant"
PASSWORD = "vehicle-1"      # as registered in Hono
HONO_MQTT_CAFILE = "certificate/c2e_hono_truststore.pem"  

# client.subscribe(f"command/{TENANT}/{DEVICE_ID}/req//speed")
# does not work, so we subscribe to all commands. Now there is two options:
# 1) filter only the alert messages here in the OBU;
# 2) filter in the Ditto <-> Hono connection (only send live messages of type "speed" to the OBU).


# TODO: Check if it is possible to only subscribe to "speed" alert messages
def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected:", rc)
    # https://eclipse.dev/hono/docs/user-guide/mqtt-adapter/
    
    # Subscribe to all commands for this device:
    # command/[${tenant-id}]/[${device-id}]/req/#
    client.subscribe(f"command/{TENANT}/{DEVICE_ID}/req/#")
    #client.subscribe("command///req/#")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"[CMD] Topic: {msg.topic}\nPayload: {payload}\n")

    # Optionally parse the twin event
    data = json.loads(payload)
    if "features" in data.get("value", {}):
        speed = data["value"]["features"]["Speed"]["properties"]["advisedSpeed"]
        print(f"Advised speed received: {speed} km/h")

    # Optional: If one wants to send a command response, the topic should be:
        # command/${tenant-id}/${device-id}/res/${req-id}/${status}

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set(HONO_MQTT_CAFILE)
client.tls_insecure_set(True)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()
