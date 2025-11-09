## Configuration of the Local Twin

Before running the agent, a virtual environment must be created and the packages from requirements.txt must be installed via pip.
The package libcairo2-dev must be installed first. 
Consequently, the following three commands are necessary to setup the agent: 

`sudo apt install -y libcairo2-dev python3-venv`
`python3 -m venv venv`
`pip install -r requirements.txt`

## How to run

To run the local twin, one can only run `local-twin.py`. But in order for local twin to work properly and send information via Hono to the Digital Twin in Ditto, the logging scripts and the data collector must be running too. These can all be run using the `supervisor.conf` file inside the main OBU folder.

## Local Twin structure

![alt text](local_twin.png)

The Local Twin aggregates information from 3 different processes (2 logging scripts and the data-collector) by listening to signals broadcasted to the system's D-Bus by those processes. Then it creates Ditto Protocol messages and sends them via Hono's MQTT adapter. The messages are then routed to Ditto and transformed into *ModemStatus*, *NetworkDelay*, and *NetworkThroughput* features of the Digital Twin. 

### Links used

https://www.freedesktop.org/wiki/Software/dbus/
https://eclipse.dev/hono/docs/user-guide/mqtt-adapter/
https://eclipse.dev/ditto/protocol-overview.html