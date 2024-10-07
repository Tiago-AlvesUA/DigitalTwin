#!/bin/bash

# Ensure environment variables are set
if [ -z "$REGISTRY_BASE_URL" ]; then
  echo "Environment variables are not set. Please run the set_hono_ditto_env.sh script first."
  exit 1
fi

# Check if the device name and auth-id are provided as arguments
if [ -z "$1" ]; then
  echo "Device name is not provided. Please specify a device name as the first argument."
  exit 1
fi

if [ -z "$2" ]; then
  echo "Authentication ID is not provided. Please specify an authentication ID as the second argument."
  exit 1
fi

DEVICE_NAME=$1
AUTH_ID=$2

# Authentication IDs should be different from each other

# Update device credentials
curl -i -k -X PUT -H "Content-Type: application/json" --data '[
{
  "type": "hashed-password",
  "auth-id": "'$AUTH_ID'",
  "secrets": [{
    "pwd-plain": "my-password"
  }]
}]' ${REGISTRY_BASE_URL:?}/v1/credentials/my-tenant/org.acme:$DEVICE_NAME
