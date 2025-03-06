# DigitalTwin


## Installing Ubuntu and configuring 5G firmware on 5G OBU

Since the OBU already has a SIM card from NOS, it is from the start in the NOS network.

Firstly need a pendrive with Ubuntu (the server version, since there is no UI).
Then to install need cable to be able to use the console. Putty on windows is easy to use, since the **baudrate** might need to be changed; Although more difficult, minicom can be used on Linux.

To install the 5G service, need to access https://gitlab.es.av.it.pt/route-25/5g-firmware and put the different files .rules, .conf, .service, .link and .network on the correct paths/folders. Then we just need to start the service by running `systemctl start it2s_5g`. An IP will be available from there.

## Dealing with NOS GCP

On GCP, more specifically in compute engine -> VM instances.
The first two VMs need to be started. 
SSH through browser for operating in the VM.