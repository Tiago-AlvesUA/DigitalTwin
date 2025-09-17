#!/bin/bash
set -e

# 1. Environment setup
curl -L https://www.eclipse.org/packages/packages/cloud2edge/scripts/setCloud2EdgeEnv.sh \
  --output setCloud2EdgeEnv.sh
chmod u+x setCloud2EdgeEnv.sh

RELEASE=c2e
NS=cloud2edge
TRUSTSTORE_PATH=/tmp/c2e_hono_truststore.pem
eval $(./setCloud2EdgeEnv.sh $RELEASE $NS $TRUSTSTORE_PATH)

# 2. Hono + Ditto setup
cd hono
./create_tenant.sh
./register_device.sh
./update_device_credentials.sh
./create_amqp_connection.sh
./create_ditto_policy.sh
./create_ditto_twin.sh
cd ..