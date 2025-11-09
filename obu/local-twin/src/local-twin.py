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
from config import HONO_BROKER_HOST, HONO_BROKER_PORT, HONO_MQTT_USERNAME, HONO_MQTT_PASSWORD, HONO_MQTT_CAFILE, HONO_MQTT_TOPIC, DITTO_THING_NAME, DITTO_THING_NAMESPACE
import socket

mqtt_client = None
device_id = None
network_delay = 0
network_throughput = [0, 0]
sample_count = 0
send_times = []


# Signal handler for clean exit
def signal_handler(sig, frame):
    print("Exiting...")
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    sys.exit(0)


def on_connect(client, userdata, flags, rc, properties=None):
    try:
        client.socket().setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        print("[MQTT] TCP_NODELAY enabled — immediate send per publish.")
    except Exception as e:
        print(f"[MQTT] Failed to set TCP_NODELAY: {e}")


# Function to set up the MQTT client
def setup_mqtt():
    global mqtt_client, device_id
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    mqtt_client.tls_set(HONO_MQTT_CAFILE)
    mqtt_client.tls_insecure_set(True)

    mqtt_client.username_pw_set(HONO_MQTT_USERNAME, HONO_MQTT_PASSWORD)

    mqtt_client.on_connect = on_connect

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

    network_throughput[0] = args[0] # rx_bytes
    network_throughput[1] = args[1] # tx_bytes

    unix_timestamp = time.time()
    timestamp = timestamp_to_its(unix_timestamp)

    jobj = {
        "topic": f"{DITTO_THING_NAMESPACE}/{DITTO_THING_NAME}/things/twin/commands/modify",
        "headers": {},
        "path": "/features/NetworkThroughput/properties",
        "value": {
            "referenceTime": timestamp,
            "rx_bytes": network_throughput[0],
            "tx_bytes": network_throughput[1]
        }
    }

    publish_to_mqtt(json.dumps(jobj))


# Callback function when a DT feature update delay signal is received from D-Bus
def on_new_esbroker_delay_available(*args):
    global network_delay, device_id
    network_delay = args[0]

    unix_timestamp = time.time()
    timestamp = timestamp_to_its(unix_timestamp)

    jobj = {
        "topic": f"{DITTO_THING_NAMESPACE}/{DITTO_THING_NAME}/things/twin/commands/modify",
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
        "topic": f"{DITTO_THING_NAMESPACE}/{DITTO_THING_NAME}/things/twin/commands/modify",
        "headers": {},
        "path": "/features/ModemStatus/properties",  
        "value": {
            "referenceTime": timestamp,
            "referencePosition": {
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

    # TODO: Create appropriate ASN.1 Structure for Ditto message

    return json.dumps(ditto_msg)


# Publish data to Hono's MQTT adapter
def publish_to_mqtt(json_data):
    global sample_count, send_times

    result = mqtt_client.publish(HONO_MQTT_TOPIC, json_data)
    
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"Published: {json_data} to {HONO_MQTT_TOPIC}")
        ### Uncomment to log reception time and delay of MCM ###
        # sample_count += 1
        # unix_time = time.time()
        # send_times.append(unix_time)
        # # Stop if sample count reached 1000
        # if sample_count >= 1000:
        #     print("Reached 1000 samples, exiting...")
        #     with open("send_times.txt", "w") as f:
        #         for t in send_times:
        #             f.write(f"{t}\n")
        #     signal_handler(None, None)
        ########################################################
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
