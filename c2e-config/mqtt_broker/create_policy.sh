#!/bin/bash

# Configuration
BASE_URL="http://localhost:8080/api/2"
AUTH="ditto:ditto"
POLICY_ID="my.test:policy"
POLICY_PAYLOAD='{
    "entries": {
        "owner": {
            "subjects": {
                "nginx:ditto": {
                    "type": "nginx basic auth user"
                }
            },
            "resources": {
                "thing:/": {
                    "grant": [
                        "READ","WRITE"
                    ],
                    "revoke": []
                },
                "policy:/": {
                    "grant": [
                        "READ","WRITE"
                    ],
                    "revoke": []
                },
                "message:/": {
                    "grant": [
                        "READ","WRITE"
                    ],
                    "revoke": []
                }
            }
        }
    }
}'

# Make API request
curl -X PUT "${BASE_URL}/policies/${POLICY_ID}" \
     -u "${AUTH}" \
     -H "Content-Type: application/json" \
     -d "${POLICY_PAYLOAD}"