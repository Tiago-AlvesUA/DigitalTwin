#!/usr/bin/python3
import sys
import json
import time
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
# import sseclient
import base64
# import requests
from websocket import WebSocketApp
from config import DITTO_WS_URL, DITTO_AUTH, DITTO_THING_NAMESPACE, DITTO_THING_NAME

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

def on_open(ws):
    print("[Ditto WS] Connection opened.")

    ditto_thing_id = f"{DITTO_THING_NAMESPACE}:{DITTO_THING_NAME}"

    ws.send(f"START-SEND-EVENTS?filter=and(eq(thingId,'{ditto_thing_id}'),eq(resource:path,'/features/ModemStatus/properties'))")

# When message is received, the delay the message took to arrive to the broker is calculated
def on_message(ws, message):
    
    if message.strip().startswith("START-SEND-EVENTS:ACK"):
        return
    
    try:
        data = json.loads(message)

        if not data.get("value"):
            return
        
        value = data.get("value")
        message_reftime = int(value["referenceTime"])
        message_gdt = message_reftime % 65536
        current_gdt = current_milli_time() % 65536

        delay_ms = 0

        if current_gdt > message_gdt:
            delay_ms = current_gdt - message_gdt
        elif current_gdt < message_gdt:
            delay_ms = current_gdt + 65536 - message_gdt
        else:
            delay_ms = 0

        pub_delay_to_dbus(delay_ms)
        
    except Exception as e:
        print(f"[Ditto WS] Error processing message: {e}")


def on_error(ws, error):
    print("[Ditto WS] Websocket error:", error)

def on_close(ws, close_status_code, close_msg):
    print("[Ditto WS] Connection closed.")

def listen():
    headers = {
        "Authorization": f"Basic {DITTO_AUTH}",
    }

    ws = WebSocketApp(
        DITTO_WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        header=headers
    )

    ws.run_forever()


def main():
    global delay_service
    system_bus = init_dbus()
    delay_service = DelayService(system_bus, "/org/example/DataReader")

    listen()

main()