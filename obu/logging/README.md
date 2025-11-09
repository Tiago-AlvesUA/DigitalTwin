### Logging folder

Contains two scripts to get network logs. `network-tt.py` obtains throughput of the network (transmitted and received bytes per second: OBU <-> Hono). `network-delay.py` calculates the delay a *ModemStatus* feature update takes to go from the vehicle to Ditto and back (the script subscribes to *ModemStatus* features updates using Ditto's WS connection).
