#!/bin/bash

# Ensure environment variables are set
if [ -z "$REGISTRY_BASE_URL" ]; then
  echo "Environment variables are not set. Please run the set_hono_ditto_env.sh script first."
  exit 1
fi

# Check if the device name is provided as an argument
if [ -z "$1" ]; then
  echo "Device name is not provided. Please specify a device name as an argument."
  exit 1
fi

DEVICE_NAME=$1

# Register a device
curl -i -k -X POST ${REGISTRY_BASE_URL:?}/v1/devices/my-tenant/org.acme:$DEVICE_NAME
