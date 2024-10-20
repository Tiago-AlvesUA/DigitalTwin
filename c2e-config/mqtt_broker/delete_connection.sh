curl -X POST "http://localhost:8080/devops/piggyback/connectivity?timeout=10000ms" \
     -u devops:60kjDL6lJNM8 \
     -H "Content-Type: application/json" \
     -d '{
    "targetActorSelection": "/system/sharding/connection",
    "headers": {
        "aggregate": false
    },
    "piggybackCommand": {
        "type": "connectivity.commands:deleteConnection",
        "connectionId": "mqtt-example-connection-123"
    }
}'