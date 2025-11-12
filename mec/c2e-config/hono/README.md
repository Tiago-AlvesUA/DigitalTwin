## AMQP Hono <-> Ditto connection targets configuration (downstream communication)

### Ditto interaction types

The four possible target topics (which correspond to the possible interaction types in Ditto) are:
1. `_/_/things/live/commands` : App -> Device live commands (always expect response)
2. `_/_/things/live/messages` : App -> Device live messages (optionally expect response, only if response-required header is set)
3. `_/_/things/twin/events` : Twin -> Device synchronization (such as feature updates)
4. `_/_/things/live/events` : Device -> App updates 

In order to only get the speed alert messages when the device subscribes to all command messages (via Hono), the AMQP 1.0 connection between Hono and Ditto, configured in Ditto, must only have the live messages as a target topic that sends commands to the devices connected to Hono:
(`"topics": ["_/_/things/live/messages"]`)

The new connection with only this topic is in script `create_amqp_connection.sh`. The previous connection, that uses all the topics is `create_amqp_connection_old.sh`.

The only topics relevant to this work are the live commands and live messages. The collision alert must go directly from the App to the Device. The live commands always expect a response from the device, while the live messages only expect a response if the response-required header is set to true.

### Connection header mappings

Header mappings in targets:
**to:** AMQP destination - Hono's address for Command&Control (e.g. command/tenant-id/device-id)
**reply-to:** Optional address where the device should send responses
**correlation-id:** Lets Ditto match responses to requests

Connections documentation: https://eclipse.dev/ditto/basic-connections.html#connection-model