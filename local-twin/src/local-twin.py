import paho.mqtt.client as mqtt
# import asn1tools
import json
import signal
import sys
import toml
import dbus
import dbus.mainloop.glib
import time
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
network_delay = 0
network_throughput = [0, 0]
# asn1_files = ['ditto_message_v3.asn1', 'cd_dictionary_ts_102_894_2_v2.2.1.asn1', 'modem_status_2.0.asn1']
# dtm = asn1tools.compile_files(asn1_files, 'jer')

# Signal handler for clean exit
def signal_handler(sig, frame):
    print("Exiting...")
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    sys.exit(0)

# Function to set up the MQTT client
def setup_mqtt():
    global mqtt_client, device_id
    # TODO: Create new toml file for the local-twin
    itss_cfg = toml.load('/etc/it2s/itss.toml')
    device_id = itss_cfg['security']['identity']['station-id']

    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    mqtt_client.tls_set(MQTT_CAFILE)
    mqtt_client.tls_insecure_set(True)

    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    mqtt_client.connect(HONO_BROKER_HOST, HONO_BROKER_PORT)
    mqtt_client.loop_start()

# Function to listen for D-Bus signals
# TODO: Change dbus interface to correct names
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

def timestamp_to_its(unix_timestamp):
    if unix_timestamp == 0:
        return 0
    # Miliseconds timestamp
    return int(((unix_timestamp + 5) * 1000) - 1072915200000)

# Callback function when a es-broker throughput signal is received from D-Bus
def on_new_esbroker_tt_available(*args):
    global network_throughput, device_id
    device_id = "my-device-2" # TODO: Now remains static but to be changed later on

    network_throughput[0] = args[0] # rx_bytes
    network_throughput[1] = args[1] # tx_bytes

    unix_timestamp = time.time()
    timestamp = timestamp_to_its(unix_timestamp)

    jobj = {
        "topic": f"org.acme/{device_id}/things/twin/commands/modify",
        "headers": {},
        "path": "/features/NetworkThroughput/properties",
        "value": {
            "referenceTime": timestamp,
            "rx_bytes": network_throughput[0],
            "tx_bytes": network_throughput[1]
        }
    }

    publish_to_mqtt(json.dumps(jobj))

# Callback function when a es-broker delay signal is received from D-Bus
def on_new_esbroker_delay_available(*args):
    global network_delay, device_id
    network_delay = args[0]
    device_id = "my-device-2" # TODO: Now remains static but to be changed later on
    
    unix_timestamp = time.time()
    timestamp = timestamp_to_its(unix_timestamp)

    jobj = {
        "topic": f"org.acme/{device_id}/things/twin/commands/modify",
        "headers": {},
        "path": "/features/MessageDelay/properties",
        "value": {
            "referenceTime": timestamp,
            "delay": network_delay
        }
    }

    publish_to_mqtt(json.dumps(jobj))

# Callback function when a data signal is received from D-Bus
def on_new_data_available(*args):
    json_data = create_modstatus_msg(args)
    publish_to_mqtt(json_data)


def create_modstatus_msg(args):
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
    # msg_sn = args[17] # Not needed now


    ditto_msg = {
        "topic": f"org.acme/{device_id}/things/twin/commands/modify",
        "headers": {},
        "path": "/features/ModemStatus/properties",  # TODO: Modify this path if necessary 
        "value": {
            "referenceTime": timestamp,
            "referencePosition": {  # TODO: RefPosition stays here for now but it might be received from the broker later, to a new feature, Localization
                "latitude": gps_latitude,
                "longitude": gps_longitude,
                "positionConfidenceEllipse": {
                    "semiMajorConfidence": 4095,
                    "semiMinorConfidence": 4095,
                    "semiMajorOrientation": 900
                },
                "altitude": {
                    "altitudeValue": gps_altitude,
                    "altitudeConfidence": "unavailable"
                }
            },
            "modemStatus": {
                "mcc": mcc,
                "mnc": mnc,
                "ratMode": ratmode,
                "nr": {
                    "rsrq": nr_rsrq,
                    "rsrp": nr_rsrp,
                    "snr": nr_snr,
                    "pci": nr_pci
                },
                "lte": {
                    "rsrq": lte_rsrq,
                    "rsrp": lte_rsrp,
                    "rssi": lte_rssi,
                    "snr": lte_snr,
                    "pci": lte_pci
                }
            }
        }
    }

    # TODO: Later on review ASN.1 Structure

    return json.dumps(ditto_msg)

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
