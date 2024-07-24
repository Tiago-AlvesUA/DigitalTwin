import subprocess
import random
import time
import json

# Configuration
# topic = "ditto-tutorial/my.test/octopus/things/twin/commands/modify"
topic = "ditto-tutorial/my.test:octopus"
publish_interval = 2  # seconds

def generate_random_values():
    temp = round(random.uniform(20.0, 40.0), 2)  # Generate random temperature between 20.0 and 40.0
    alt = round(random.uniform(100.0, 500.0), 2)  # Generate random altitude between 100.0 and 500.0
    return temp, alt

def build_ditto_protocol_msg(thing_id, temp, alt):
    namespace, name = thing_id.split(':')

    value = {
        "temp_sensor": {
            "properties": {
                "value": temp
            }
        },
        "altitude": {
            "properties": {
                "value": alt
            }
        }
    }

    # Construct the Ditto Protocol message
    ditto_message = {
        "topic": build_topic(namespace, name, 'things', 'twin', 'commands', 'modify'),
        "path": "/features",
        "headers": {}, 
        "value": value
    }

    return ditto_message

def build_topic(namespace, name, group, channel, criterion, action):
    return f"{namespace}/{name}/{group}/{channel}/{criterion}/{action}"

def publish_message(message, broker_host, port="1883"):
    message_str = json.dumps(message)
    subprocess.run(["mosquitto_pub", "-h", broker_host, "-t", topic, "-p", port, "-m", message_str])

def main():
    broker_host = input("Enter the broker host (localhost, test.mosquitto.org, etc.): ")

    while True:
        temp, alt = generate_random_values()
        thing_id = "my.test:octopus"
        ditto_message = build_ditto_protocol_msg(thing_id, temp, alt)
        publish_message(ditto_message, broker_host)
        print(f"Published: {json.dumps(ditto_message, indent=2)}")
        time.sleep(publish_interval)

if __name__ == "__main__":
    main()
