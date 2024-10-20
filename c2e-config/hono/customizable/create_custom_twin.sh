#!/bin/bash

# Ensure environment variables are set
if [ -z "$DITTO_API_BASE_URL" ]; then
  echo "Environment variables are not set. Please run the set_hono_ditto_env.sh script first."
  exit 1
fi

# Default device name
DEFAULT_DEVICE_NAME="my-device-1"

# Read input parameters: first parameter is the device name, remaining are feature definitions
DEVICE_NAME=${1:-$DEFAULT_DEVICE_NAME}
shift  # Shift to remove the first argument (device name) and leave only the features

# Check if features were provided
if [ "$#" -eq 0 ]; then
  echo "Please provide at least one feature with properties."
  exit 1
fi

# Generate features JSON
FEATURES_JSON="{"
while (( "$#" )); do
  # Expect the feature name first
  FEATURE_NAME=$1
  shift  # Move to properties
  
  # Start feature JSON
  FEATURE_JSON="\"$FEATURE_NAME\": {\"properties\": {"
  
  # Add all key-value properties until we hit the next feature (or run out of args)
  while (( "$#" )); do
    case $1 in
      *=*)
        # It's a key-value pair (property), so extract key and value
        PROP_KEY=$(echo "$1" | cut -d '=' -f 1)
        PROP_VALUE=$(echo "$1" | cut -d '=' -f 2)
        
        # Check if the value is a number or a string
        if [[ "$PROP_VALUE" =~ ^-?[0-9]+([.][0-9]+)?$ ]]; then
          # Numeric value, no quotes
          FEATURE_JSON+="\"$PROP_KEY\": $PROP_VALUE,"
        else
          # String value, add quotes
          FEATURE_JSON+="\"$PROP_KEY\": \"$PROP_VALUE\","
        fi
        shift
        ;;
      *)
        # It's not a key-value pair, assume it's a new feature name, break the loop
        break
        ;;
    esac
  done
  
  # Close the properties object (remove the trailing comma if present)
  FEATURE_JSON="${FEATURE_JSON%,}}},"
  
  # Append the generated feature JSON
  FEATURES_JSON+="$FEATURE_JSON"
done

# Close the features JSON object (remove the trailing comma if present)
FEATURES_JSON="${FEATURES_JSON%,}}"

# Create the digital twin in Ditto
curl -i -X PUT -u ditto:ditto -H 'Content-Type: application/json' --data '{
  "policyId": "org.acme:my-policy",
  "attributes": {
    "location": "Portugal"
  },
  "features": '"${FEATURES_JSON}"'
}' "${DITTO_API_BASE_URL:?}/api/2/things/org.acme:${DEVICE_NAME}"
