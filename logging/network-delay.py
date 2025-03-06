#!/usr/bin/python3
import sys
import ssl
import json
import time
import paho.mqtt.client as mqtt
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib

broker_address = "es-broker.av.it.pt"
broker_port = 8884
broker_sub_topic = "its_center/inqueue/json/20/CAM/#"
broker_pub_topic = "logs/21/DELAY"
broker_client_id = "delay_logger_mqtt_20"
broker_certfile_path = "/etc/it2s/mqtt/it2s-station.crt"
broker_keyfile_path = "/etc/it2s/mqtt/it2s-station.key"
broker_cafile_path = "/etc/it2s/mqtt/ca.crt"
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, broker_client_id)

system_bus = None

class DelayService(dbus.service.Object):
    """ Set up the D-Bus object """
    def __init__(self, conn, object_path):
        dbus.service.Object.__init__(self, conn, object_path)

    """ Define the signal """
    @dbus.service.signal(dbus_interface="org.example.DataReader", signature="i")
    def NewDelayAvailable(self, delay):
        print(f"New delay available: {delay}")


def current_milli_time():
    return (round(time.time() * 1000) + 5000) - 1072915200000
    
def init_dbus():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    try:
        system_bus = dbus.SystemBus()
    except Exception as e:
        print(f"Failed to connect to the system bus: {e}")
        sys.exit(1)

    return system_bus


def pub_delay_to_dbus(delay, system_bus):
    global delay_service
    
    try:
        delay_service.NewDelayAvailable(dbus.Int32(delay))
    except Exception as e:
        print(f"Failed to publish delay to D-Bus: {e}")
        sys.exit(1)

    print(f"Published delay of {delay} to D-Bus")

# When message is received, the delay the message took to arrive to the broker is calculated
def on_message(client, userdata, message):
    payload_json = json.loads(message.payload)

    message_gdt = int(payload_json["cam"]["generationDeltaTime"])
    current_gdt = current_milli_time() % 65536
    delay_ms = 0

    if (current_gdt > message_gdt):
        delay_ms = current_gdt - message_gdt
    elif (current_gdt < message_gdt):
        delay_ms = current_gdt + 65536 - message_gdt
    else:
        delay_ms = 0

    pub_delay_to_dbus(delay_ms, system_bus)

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print("failed to connect")

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"broker granted the following QoS: {reason_code_list[0].value}")

def main():
    global system_bus, delay_service
    system_bus = init_dbus()
    delay_service = DelayService(system_bus, "/org/example/DataReader")

    client.username_pw_set(username="admin", password="t;RHC_vi")

    client.tls_set(
        certfile=broker_certfile_path,
        keyfile=broker_keyfile_path,
        ca_certs=broker_cafile_path,
    )
    #client.tls_insecure_set(True)

    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.connect(broker_address, broker_port)

    print("subscribing to " + broker_sub_topic)
    client.subscribe(broker_sub_topic)

    client.loop_forever()

main()
