# 5G OBU Setup

In this document, it is specified how the Advantech FWA-1112VC device was configured. The configuration included installing the OS and then setting up the 5G firmware. 

## Operative System

First, there is the need of installing the OS in the device. The choice was Ubuntu 22.04.5 (Jammy Jellyfish), since it has long-term support (LTS), is more stable, and is more reliable.

It was installed the server install image, as there will be no graphical user interface.

To configure the system both Minicom (on Linux) or PuTTY (on Windows), which are both terminal emulators. PuTTY is easier to learn so it was the chosen one.

Since there is no graphical interface, to select the pen drive with Linux, we need to enter the BIOS by Serial Console. First we need to search for the serial port (COMx, such as COM3) we will use for the connection. After finding it, the baud rate must be selected.

Baud rate is the speed at which data is transmitted over a serial connection. If not set correctly, the hardware will not handle the data right and the characters may be garbled or missing. The default baud rate for many Advantech devices and overall modern Linux serial consoles is 115200 bps. So this was the selected baud rate.

After starting the serial port connection on putty, the common steps to install Ubuntu on a device were performed. Choosing language/keyboard layout, set disk partitioning, create user & password, configure network (the device was connected to IT ethernet since the start), and finally conclude installation.

## 5G Setup

Now that the OS is installed we can go through the 5G firmware setup. Different files were copied from https://gitlab.es.av.it.pt/route-25/5g-firmware to the OBU, which contained:

- A it2s-5g.service file which is a systemd service that manages the 5G modules, ensures it connects properly and remains connected; it makes sure QMI dependencies exist on the system;
QMI (Qualcomm MSM Interface) is a protocol that allows communication between a host system and a Qualcomm-based cellular modem to control, configure, and manage mobile broadband like 5G. It is an alternative to the traditional and less efficient AT commands.
The commands are applied via the QMI control interface, namely /dev/cdc-wdm0. The qmicli commands used here configure things such as setting APN (Access Point Name) settings and starting the network connection. The APN is huawey.com as NOS uses huawey routers.

- The 05-it2s-5g.link file ensures the network interface name of the 5G module is always it2s-5g instead of the generic wwan0;

- The 99-it2s_5g-network file configures the network settings for it2s_5g, ensuring it uses DHCP for automatic IP configuration and DNS settings provided by DHCP. It also disables unnecessary local addressing;

- The 10-it2s-5g.rules file has the purpose to start the it2s-5g.service as the modem is plugged in and remove it when unplugged.

- Finally the qmi-network.conf contains the APN and proxy usage.

Together, these files allow the configuration of the 5G modem to be configured, and establish a network connection using QMI. Before starting the 5G service some AT commands were executed to previously configure the modem to enable auto selection of internal operator-specific configuration by reading the SIM network. This network corresponded to NOS network, the same network where the cloud ditto will be present. This was this 5G OBU, representing the real vehicle can directly contact with its digital counterpart on the same network. After the AT commands, there was just a task left of starting the service. The 5G network interface appeard, with a NOS IP assigned.