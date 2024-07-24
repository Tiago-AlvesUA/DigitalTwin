import subprocess
import random
import time
import json

# Configuration

# broker_host = "test.mosquitto.org"
topic = "ditto-tutorial/my.test:octopus"
thing_id = "my.test:octopus"
publish_interval = 2  # seconds

def generate_random_values():
    temp = round(random.uniform(20.0, 40.0), 2)  # Generate random temperature between 20.0 and 40.0
    alt = round(random.uniform(100.0, 500.0), 2)  # Generate random altitude between 100.0 and 500.0
    return temp, alt

def publish_message(temp, alt, broker_host, port="1883"):
    message = {
        "temp": temp,
        "alt": alt,
        "thingId": thing_id
    }
    message_str = json.dumps(message)
    subprocess.run(["mosquitto_pub", "-h", broker_host, "-t", topic, "-p", port, "-m", message_str])

def main():
    # ask for the broker host
    broker_host = input("Enter the broker host (localhost, test.mosquitto.org, etc.): ")

    while True:
        temp, alt = generate_random_values()
        publish_message(temp, alt, broker_host)
        print(f"Published: temp={temp}, alt={alt}")
        time.sleep(publish_interval)

if __name__ == "__main__":
    main()
