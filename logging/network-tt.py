#!/usr/bin/python3
import json
import paho.mqtt.client as mqtt
from scapy.all import *
from threading import Thread
import sys
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib

broker_certfile_path = "/etc/it2s/mqtt/it2s-station.crt"
broker_keyfile_path = "/etc/it2s/mqtt/it2s-station.key"
broker_cafile_path = "/etc/it2s/mqtt/ca.crt"
broker_address = "es-broker.av.it.pt"
broker_port = 8884

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "network_logger_mqtt_21")
mqtt_client.username_pw_set(username="admin", password="t;RHC_vi")
mqtt_client.tls_set(certfile=broker_certfile_path, keyfile=broker_keyfile_path, ca_certs=broker_cafile_path)
mqtt_client.connect(broker_address, broker_port)

all_ips = [iface.ip for iface in ifaces.values() if iface.name == "it2s_5g"]
traffic = [0, 0]
running = 1

system_bus = None

class TTService(dbus.service.Object):
    def __init__(self, conn, object_path):
        dbus.service.Object.__init__(self, conn, object_path)

    @dbus.service.signal(dbus_interface="org.example.DataReader", signature="ii")
    def NewThroughputAvailable(self, rx_bytes, tx_bytes):
        print(f"New Throughput available: RX: {rx_bytes} TX: {tx_bytes}")

def init_dbus():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    try:
        system_bus = dbus.SystemBus()
    except Exception as e:
        print(f"Failed to connect to the system bus: {e}")
        sys.exit(1)

    return system_bus

def pub_tt_to_dbus(rx_bytes, tx_bytes):
    global throughput_service
    try:
        throughput_service.NewThroughputAvailable(dbus.Int32(rx_bytes), dbus.Int32(tx_bytes))
    except Exception as e:
        print(f"Failed to publish throughput to D-Bus: {e}")
        sys.exit(1)

    print(f"Published throughput to D-Bus: RX: {rx_bytes} TX: {tx_bytes}")

def process_packet(packet):
    global traffic
    print("{}: {}".format(len(packet), packet.summary()))

    if packet.src in all_ips:
        traffic[1] += len(packet)
    elif (packet.dst in all_ips):
        traffic[0] += len(packet)

def process_data():
    global traffic
    
    while running:
        try:
            build_message()
            # mqtt_client.publish("logs/21/THROUGHPUT", mqtt_message)
        except:
            continue

        traffic = [0, 0]
        time.sleep(1)
        
def build_message():
    global traffic

    data = {}
    data["rx_bytes"] = traffic[0]
    data["tx_bytes"] = traffic[1]
    pub_tt_to_dbus(data["rx_bytes"], data["tx_bytes"])
    # json_data = json.dumps(data)
    # return json_data

if __name__ == "__main__":
    system_bus = init_dbus()
    throughput_service = TTService(system_bus, "/org/example/DataReader")

    processing_thread = Thread(target=process_data)
    processing_thread.start()

    sniff(prn=process_packet, store=False, filter="src port 8884 or dst port 8884")

    running = 0
    processing_thread.join()
