#!/usr/bin/python3
import sys
import json
import time
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import sseclient
import base64
import requests

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

def pub_delay_to_dbus(delay):
    global delay_service
    
    try:
        delay_service.NewDelayAvailable(dbus.Int32(delay))
    except Exception as e:
        print(f"Failed to publish delay to D-Bus: {e}")
        sys.exit(1)

    print(f"Published delay of {delay} to D-Bus")

# When message is received, the delay the message took to arrive to the broker is calculated
def handle_message(data):
    try:
        payload_json = json.loads(data)

        message_reftime = int(payload_json["properties"]["referenceTime"])

        message_gdt = message_reftime % 65536
        current_gdt = current_milli_time() % 65536

        delay_ms = 0

        if (current_gdt > message_gdt):
            delay_ms = current_gdt - message_gdt
        elif (current_gdt < message_gdt):
            delay_ms = current_gdt + 65536 - message_gdt
        else:
            delay_ms = 0

        pub_delay_to_dbus(delay_ms)
    except Exception as e:
        print(f"Error handling message: {e}")


def listen():
    auth = "ditto:ditto"
    b64_auth = base64.b64encode(auth.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Accept": "text/event-stream"
    }

    url = "http://10.255.41.221:8080/api/2/things/org.acme:my-device-2/features/ModemStatus"

    client = sseclient.SSEClient(url, headers=headers)

    for event in client:
        print(event.data)
        handle_message(event.data)


def main():
    global delay_service
    system_bus = init_dbus()
    delay_service = DelayService(system_bus, "/org/example/DataReader")

    listen()

main()
