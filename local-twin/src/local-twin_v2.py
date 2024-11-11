import paho.mqtt.client as mqtt
import asn1tools
import json
import signal
import sys
import toml
import dbus
import dbus.mainloop.glib
from gi.repository import GLib

# MQTT Configuration
HONO_BROKER_HOST = "10.255.41.221"
HONO_BROKER_PORT = 8883
# auth_id@tenant
MQTT_USERNAME = "my-auth-id-2@my-tenant"
MQTT_PASSWORD = "my-password"
MQTT_TOPIC = "telemetry"
MQTT_CAFILE = "../certificate/c2e_hono_truststore.pem"

mqtt_client = None
device_id = None
es_broker_delay = 0
es_broker_throughput = [0, 0]
ditto_asn1 = asn1tools.compile_files('ditto_message.asn1', 'jer')

# Signal handler for clean exit
def signal_handler(sig, frame):
    print("Exiting...")
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    sys.exit(0)

# Function to set up the MQTT client
def setup_mqtt():
    global mqtt_client, device_id
    itss_cfg = toml.load('/etc/it2s/itss.toml')
    device_id = itss_cfg['security']['identity']['station-id']

    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    mqtt_client.tls_set(MQTT_CAFILE)
    mqtt_client.tls_insecure_set(True)

    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    mqtt_client.connect(HONO_BROKER_HOST, HONO_BROKER_PORT)
    mqtt_client.loop_start()

# Function to listen for D-Bus signals
def listen_for_signals():
    bus = dbus.SystemBus()
    bus.add_signal_receiver(on_new_data_available,
                             dbus_interface="org.example.DataReader",
                             signal_name="NewDataAvailable")
    bus.add_signal_receiver(on_new_esbroker_delay_available,
                             dbus_interface="org.example.DataReader",
                             signal_name="NewDelayAvailable")
    bus.add_signal_receiver(on_new_esbroker_tt_available,
                             dbus_interface="org.example.DataReader",
                             signal_name="NewThroughputAvailable")

def on_new_esbroker_tt_available(*args):
    global es_broker_throughput, device_id
    #device_id = "my-device-2" # Now remains static but to be changed later on

    #rx_bytes = args[0]
    es_broker_throughput[0] = args[0]
    #tx_bytes = args[1]
    es_broker_throughput[1] = args[1]

    # jobj = {
    #     "topic": f"org.acme/{device_id}/things/twin/commands/modify",
    #     "headers": {},
    #     "path": "/features/es_broker_throughput/properties",
    #     "value": {
    #         "rx_bytes": rx_bytes,
    #         "tx_bytes": tx_bytes
    #     }
    # }

    # publish_to_mqtt(json.dumps(jobj))

# Callback function when a es-broker delay signal is received from D-Bus
def on_new_esbroker_delay_available(*args):
    global es_broker_delay, device_id
    es_broker_delay = args[0]
    #device_id = "my-device-2" # Now remains static but to be changed later on

    # jobj = {
    #     "topic": f"org.acme/{device_id}/things/twin/commands/modify",
    #     "headers": {},
    #     "path": "/features/es_broker_delay/properties/message_delay",
    #     "value": es_broker_delay
    # }

    # publish_to_mqtt(json.dumps(jobj))

# Callback function when a data signal is received from D-Bus
def on_new_data_available(*args):
    json_data = create_json_structure(args)
    publish_to_mqtt(json_data)


def create_json_structure(args):
    global device_id
    print("Previous device ID: ", device_id)
    device_id = "my-device-2" # Now remains static but to be changed later on 

    gps_latitude = args[0]
    gps_longitude = args[1]
    gps_altitude = args[2]
    ratmode = args[3]
    lte_rssi = args[4]
    lte_rsrq = args[5]
    cid = args[6]
    lte_rsrp = args[7]
    nr_rsrp = args[8]
    lte_snr = args[9]
    nr_snr = args[10]
    nr_rsrq = args[11]
    mcc = args[12]
    mnc = args[13]
    lte_pci = args[14]
    nr_pci = args[15]
    timestamp = args[16]
    msg_sn = args[17]
    
    # Create the ASN.1 structure as a Python dictionary
    ditto_msg = {
        "topic": f"org.acme/{device_id}/things/twin/commands/modify",
        "headers": {},
        "path": "/features/localTwin/properties",   # TODO: Modify this path if necessary
        "value": {
            "referencePosition": {
                "properties": {
                    "latitude": gps_latitude,
                    "longitude": gps_longitude,
                    "altitude": gps_altitude
                }
            },
            "modemStatus": {
                "properties": {
                    "mcc": mcc,
                    "mnc": mnc
                }
            },
            "nrModemStatus": {
                "properties": {
                    "rsrp": nr_rsrp,
                    "rsrq": nr_rsrq,
                    "snr": nr_snr,
                    "pci": nr_pci
                }
            },
            "lteModemStatus": {
                "properties": {
                    "rsrp": lte_rsrp,
                    "rsrq": lte_rsrq,
                    "snr": lte_snr,
                    "pci": lte_pci,
                    "rssi": lte_rssi
                }
            },
            "body": {
                "properties": {
                    "generationDeltaTime": timestamp,
                    "sequenceNumber": msg_sn
                }
            },
            "esBrokerDelay": {
                "properties": {
                    "messageDelay": es_broker_delay
                }
            },
            "esBrokerThroughput": {
                "properties": {
                    "rxBytes": es_broker_throughput[0],
                    "txBytes": es_broker_throughput[1]
                }
            }
        }
    }

    # Encode the structure with ASN.1 and convert to JSON
    encoded_data = ditto_asn1.encode('DITTO-MSG', ditto_msg)

    print(f"\n\nEncoded data: {encoded_data}")

    decoded_data = ditto_asn1.decode('DITTO-MSG', encoded_data)

    print(f"Decoded data: {decoded_data}\n\n")

    return json.dumps(decoded_data)

# Publish data to Hono's MQTT adapter
def publish_to_mqtt(json_data):
    # Publish the JSON data to the specified topic
    result = mqtt_client.publish(MQTT_TOPIC, json_data)
    
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"Published: {json_data} to {MQTT_TOPIC}")
    else:
        print(f"Failed to publish data: {result.rc}")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C for graceful shutdown
    
    # Initialize D-Bus main loop
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    
    setup_mqtt()  # Set up MQTT client
    listen_for_signals()  # Listen for D-Bus signals

    print("Listening for D-Bus signals...")
    
    # Run the main loop
    loop = GLib.MainLoop()
    loop.run()
