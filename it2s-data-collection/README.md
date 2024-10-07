# IT2S Data Collection
This repository contains code related to processing the all the sensorial data collected by the OBU and composing Ditto structure messages.

## Notes
* The messages are currently sent to a hono MQTT adapter in the cloud.
* There is also a ReferenceLocation built with data from /dev/it2s-gps.

## How to release qmi clients:
```
qmicli -d /dev/cdc-wdm0 --nas-noop --client-cid=9
```
