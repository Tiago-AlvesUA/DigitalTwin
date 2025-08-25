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

all_ips = [iface.ip for iface in ifaces.values() if iface.name == "it2s_5g"]
traffic = [0, 0]
running = 1
system_bus = None

class TTService(dbus.service.Object):
    """ Set up the D-Bus object """
    def __init__(self, conn, object_path):
        dbus.service.Object.__init__(self, conn, object_path)

    """ Define the signal """
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
    print("Packet ({}): Source: {} Destination: {}: {}".format(len(packet), packet.src, packet.dst, packet.summary()))
    
    if (packet["IP"].src in all_ips):
        traffic[1] += len(packet)
    elif (packet["IP"].dst in all_ips):
        traffic[0] += len(packet)

def process_data():
    global traffic
    
    while running:
        try:
            build_message()
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

if __name__ == "__main__":
    system_bus = init_dbus()
    throughput_service = TTService(system_bus, "/org/example/DataReader")

    print("Network IPs: " +str(all_ips))
    processing_thread = Thread(target=process_data)
    processing_thread.start()

    # Port 8883 -> MQTT messages to Eclipse Hono MQTT adapter
    sniff(prn=process_packet, store=False, filter="src port 8883 or dst port 8883")

    running = 0
    processing_thread.join()
