#!/bin/bash

# Ensure environment variables are set
if [ -z "$DITTO_API_BASE_URL" ]; then
  echo "Environment variables are not set. Please run the set_hono_ditto_env.sh script first."
  exit 1
fi

# Create the digital twin in Ditto
curl -i -X PUT -u ditto:ditto -H 'Content-Type: application/json' --data '{
  "policyId": "org.acme:my-policy",
  "attributes": {
    "location": "Germany"
  },
  "features": {
    "temperature": {
      "properties": {
        "value": null
      }
    },
    "humidity": {
      "properties": {
        "value": null
      }
    }
  }
}' ${DITTO_API_BASE_URL:?}/api/2/things/org.acme:my-device-1
