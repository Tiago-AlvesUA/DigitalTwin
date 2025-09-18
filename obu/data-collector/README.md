# IT2S Data Collection
This repository contains code related to processing the all the sensorial data collected by the OBU and composing VSMs.

## Notes
* The messages are currently sent to a MQTT broker in the cloud.
* Currently VSMs are composed by a OVSM/SPVSM/SNVSM bodies:
    * OVSM Body: Composed with the data from /dev/it2s-obd.
    * SPVSM Body: Composed with the data from /dev/it2s-smartphone.
    * SNVSM Body: Composed with the data from /dev/it2s-sonar.
* There is also a ReferenceLocation built with data from /dev/it2s-gps.

## How to release qmi clients:
```
qmicli -d /dev/cdc-wdm0 --nas-noop --client-cid=9
```
