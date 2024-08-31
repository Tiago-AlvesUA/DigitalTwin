#!/bin/bash

# Configuration
BASE_URL="http://localhost:8080/api/2"
AUTH="ditto:ditto"
THING_ID="my.test:octopus"
THING_PAYLOAD='{
    "policyId": "my.test:policy",
    "attributes": {
        "name": "octopus",
        "type": "octopus board"
    },
    "features": {
        "temp_sensor": {
            "properties": {
                "value": 0
            }
        },
        "altitude": {
            "properties": {
                "value": 0
            }
        }
    }
}'

# Make API request
curl -X PUT "${BASE_URL}/things/${THING_ID}" \
     -u "${AUTH}" \
     -H "Content-Type: application/json" \
     -d "${THING_PAYLOAD}"