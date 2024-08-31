#!/bin/bash

cd hono

# Step 1: Set environment variables
# Follow set_env_variables.txt

# Step 2: Create tenant in Hono
./create_tenant.sh
echo
# Step 3: Register device in Hono
./register_device.sh
echo
# Step 4: Update device credentials in Hono
./update_device_credentials.sh

# Step 5: Create connection in Ditto
./create_amqp_connection.sh

# Step 6: Create policy in Ditto
./create_ditto_policy.sh

# Step 7: Create digital twin in Ditto
./create_ditto_twin.sh

# Step 8: Create new environment and set authentication in Ditto UI
# Step 9: Start sending telemetry data to Hono