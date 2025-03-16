BROKER_HOST = "es-broker.av.it.pt"
BROKER_PORT = 8090
MQTT_INITIAL_TOPIC = "its_center/inqueue/json/22/#" # TODO: Usage of geographical tiling here
MQTT_USERNAME = "it2s"
MQTT_PASSWORD = "it2sit2s"

DITTO_BASE_URL = "http://localhost:8080/api/2/things"
DITTO_THING_ID = "org.acme:my-device-1" # TODO: This can be dynamic (getting the device name), from the toml file
DITTO_USERNAME = 'ditto'
DITTO_PASSWORD = 'ditto'

WS_HOST = "localhost"
WS_PORT = 8765