import queue
import paho.mqtt.client as mqtt

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport='websockets')

last_local_perception_update = 0
last_local_awareness_update = 0
last_local_trajectories_update = 0

message_queue = queue.Queue()
