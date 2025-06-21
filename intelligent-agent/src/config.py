BROKER_HOST = "es-broker.av.it.pt"
BROKER_PORT = 8090
# TODO: I put id 201 but it should be 22/201, but better is dynamic
MQTT_INITIAL_TOPIC = "its_center/inqueue/json/22/#"
MQTT_USERNAME = "it2s"
MQTT_PASSWORD = "it2sit2s"

#DITTO_BASE_URL = "http://localhost:8080/api/2/things"
DITTO_BASE_URL = "http://10.255.41.221:8080/api/2/things"
DITTO_WS_URL = "http://10.255.41.221:8080/ws/2"
#DITTO_THING_ID = "org.acme:my-device-1" # TODO: This can be dynamic (getting the device name), from the toml file
DITTO_THING_ID = "org.acme:my-device-2" # TODO: This can be dynamic (getting the device name), from the toml file
DITTO_USERNAME = 'ditto'
DITTO_PASSWORD = 'ditto'

WS_HOST = "localhost"
WS_PORT = 8765