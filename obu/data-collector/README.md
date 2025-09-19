# IT2S Data Collection
This repository contains code related to processing the all the sensorial data collected by the OBU.

## Installation
- Data-collector relies on some packages to compile:  
    - gcc, g++, cmake, make, pkg-config
    - libglib2.0-dev, libmbim-glib-dev, libqmi-glib-dev, libjson-c-dev
    - it2s-itss-git

> The last one is because of it2s-gnss.h library. In order to obtain the last package the It2s repository GPG key must be retrieved and then, the It2s repository `https://es.av.it.pt/repo` must be added to apt sources list.
Example: `echo "deb [arch=amd64] https://es.av.it.pt/repo/ubuntu/noble stable main" > /etc/apt/sources.list.d/it2s.list`

## Compilation
- Run the following commands:
    - mkdir build, cd build
    - cmake ..
    - make

## Notes
* The messages (signals) are currently sent to the system D-Bus message bus;
* Local-twin is listening for these signals and sends them to Eclipse Ditto in MEC;
* Makes use of qmi to communicate and extract modem information;


## How to release qmi clients:
```
qmicli -d /dev/cdc-wdm0 --nas-noop --client-cid=9
```
