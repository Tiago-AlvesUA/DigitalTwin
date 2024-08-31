# Configuration of Digital Twin
## Option 1: With Hono and Ditto

### Step 1 - Set the environment
Download the script from c2e packages, define and set the environment variables and finally, execute the script:

    curl https://www.eclipse.org/packages/packages/cloud2edge/scripts/setCloud2EdgeEnv.sh \
    --output setCloud2EdgeEnv.sh
    chmod u+x setCloud2EdgeEnv.sh

    RELEASE=c2e
    NS=cloud2edge
    # file path that the Hono example truststore will be written to
    TRUSTSTORE_PATH=/tmp/c2e_hono_truststore.pem
    eval $(./setCloud2EdgeEnv.sh $RELEASE $NS $TRUSTSTORE_PATH)


### Step 2 - Hono and Ditto configurations
To fully configure Hono and Ditto, six scripts were created. These scripts are located in the `hono` folder and can be executed collectively using the `./full_hono_ditto_setup.sh` script.

The scripts using hono's API create a tenant (group of devices with certain characteristics), register a device for that tenant and lastly, update the device credentials. The ones using ditto's API create a policy, digital twin and to conclude, an AMQP connection between hono and ditto.

### Step 3 - Test connection

Publish a message to hono's MQTT adapter to modify the temperature of the twin:

    mosquitto_pub -d -h ${MQTT_ADAPTER_IP} -p ${MQTT_ADAPTER_PORT_MQTTS} -u my-auth-id-1@my-tenant -P my-password ${MOSQUITTO_OPTIONS} -t telemetry -m '{
    "topic": "org.acme/my-device-1/things/twin/commands/modify",
    "headers": {},
    "path": "/features/temperature/properties/value",
    "value": 5000
    }'

## Option 2: Direct connection from Ditto to Broker

### Step 1
In order to fully configure Ditto and create a connection with the broker, three scripts were created. They include creating a connection, policy and finally, the digital twin. These scripts are located in the `mqtt_broker` folder and can be executed collectively using the `./full_broker_ditto_setup.sh` script.


