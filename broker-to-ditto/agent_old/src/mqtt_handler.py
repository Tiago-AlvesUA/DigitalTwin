from config import BROKER_HOST, BROKER_PORT, MQTT_USERNAME, MQTT_PASSWORD, MQTT_INITIAL_TOPIC
from message_processing import process_message
import global_vars

def on_message_cb(client, userdata, message):     
    process_message(client, userdata, message)
 
def on_connect_cb(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print("failed to connect")

    print("Subscribing to topic: " + MQTT_INITIAL_TOPIC)
    global_vars.mqtt_client.subscribe(MQTT_INITIAL_TOPIC)

def setup_initial_mqtt():
    global_vars.mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    global_vars.mqtt_client.on_message = on_message_cb
    global_vars.mqtt_client.on_connect = on_connect_cb
    global_vars.mqtt_client.connect(BROKER_HOST, BROKER_PORT)