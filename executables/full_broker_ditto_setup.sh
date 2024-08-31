#!/bin/bash

cd mqtt_broker

# Step 1: Create connection in Ditto
./create_connection.sh

# Step 2: Create policy in Ditto
./create_policy.sh

# Step 3: Create digital twin in Ditto
./create_twin.sh

# Step 4: Create new environment and set authentication in Ditto UI
# Step 5: Start sending telemetry data