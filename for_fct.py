import requests
import random
import time

# Configuration
BASE_URL = "http://10.255.41.197:8080/api/2/things/org.acme:vehicle-1"
AUTH = ("ditto", "ditto")  # Replace with your actual username and password
HEADERS = {"Content-Type": "application/merge-patch+json"}

reference_time_modem = 3222087000
reference_time_delay = 664219700000
reference_time_throughput = 664216400000

def generate_random_data():
    """Generate random values for the twin's properties."""
    global reference_time_modem, reference_time_delay, reference_time_throughput
    
    # Increment reference times
    reference_time_modem += random.randint(1, 5)
    reference_time_delay += random.randint(1000, 5000)
    reference_time_throughput += random.randint(1000, 5000)

    return {
        "features": {
            "ModemStatus": {
                "properties": {
                    "referenceTime": reference_time_modem,
                    "referencePosition": {
                        "latitude": random.randint(406000000, 407000000),  # Simulated latitude
                        "longitude": random.randint(-87000000, -86000000),  # Simulated longitude
                        "positionConfidenceEllipse": {
                            "semiMajorConfidence": random.randint(4000, 4150),
                            "semiMinorConfidence": random.randint(4000, 4150),
                            "semiMajorOrientation": random.randint(300, 360)
                        },
                        "altitude": {
                            "altitudeValue": random.randint(20, 100),
                            "altitudeConfidence": random.choice(["unavailable", "low", "high"])
                        }
                    },
                    "modemStatus": {
                        "mcc": 3,
                        "mnc": 268,
                        "ratMode": 8,  # Example radio modes
                        "nr": {
                            "rsrq": random.randint(-12, -9),  
                            "rsrp": random.randint(-70, -60), 
                            "snr": random.randint(30, 40),  
                            "pci": 0
                        },
                        "lte": {
                            "rsrq": random.randint(-120, -100),
                            "rsrp": random.randint(-50, -40),
                            "rssi": random.randint(-90, -65),
                            "snr": random.randint(70, 90),
                            "pci": 297
                        }
                    }
                }
            },
            "MessageDelay": {
                "properties": {
                    "referenceTime": reference_time_delay,
                    "delay": random.randint(4, 15)
                }
            },
            "NetworkThroughput": {
                "properties": {
                    "referenceTime": reference_time_throughput,
                    "rx_bytes": random.randint(1000, 1900),
                    "tx_bytes": random.randint(1000, 1900)
                }
            }
        }
    }

def send_update():
    """Send a random update to the twin."""
    data = generate_random_data()
    try:
        response = requests.patch(BASE_URL, json=data, auth=AUTH, headers=HEADERS)
        if response.status_code == 204:
            print("Update successful:", data)
        else:
            print("Failed to update. Status:", response.status_code, "Response:", response.text)
    except Exception as e:
        print("Error sending update:", e)

def main():
    """Send updates at random intervals."""
    while True:
        send_update()
        time.sleep(0.2) 

if __name__ == "__main__":
    main()
