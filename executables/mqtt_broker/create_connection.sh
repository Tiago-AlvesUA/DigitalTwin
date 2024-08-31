#!/bin/bash

# Configuration
BASE_URL="http://localhost:8080/devops/piggyback/connectivity"
AUTH="devops:60kjDL6lJNM8"
TIMEOUT="10000ms"
CONNECTION_PAYLOAD='{
    "targetActorSelection": "/system/sharding/connection",
    "headers": {
        "aggregate": false
    },
    "piggybackCommand": {
        "type": "connectivity.commands:createConnection",
        "connection": {
            "id": "mqtt-example-connection-123",
            "connectionType": "mqtt",
            "connectionStatus": "open",
            "failoverEnabled": true,
            "uri": "tcp://172.16.10.11:1883",
            "sources": [{
                "addresses": ["ditto-tutorial/#"],
                "authorizationContext": ["nginx:ditto"],
                "qos": 0,
                "filters": []
            }],
            "targets": [{
                "address": "ditto-tutorial/{{ thing:id }}",
                "topics": [
                    "_/_/things/twin/events",
                    "_/_/things/live/messages"
                ],
                "authorizationContext": ["nginx:ditto"],
                "qos": 0
            }]
        }
    }
}'

# Make API request
curl -X POST "${BASE_URL}?timeout=${TIMEOUT}" \
     -u "${AUTH}" \
     -H "Content-Type: application/json" \
     -d "${CONNECTION_PAYLOAD}"