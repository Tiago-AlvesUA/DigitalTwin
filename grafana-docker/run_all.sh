#!/bin/sh

#TODO: This bruh
chown -R 472:472 /var/lib/grafana/plugins

# ls -la /var/lib/grafana/plugins > /log.txt
cd /var/lib/grafana/plugins/grafana-app-opentwins/src/

yarn install

yarn dev &

sleep 5

cd /usr/share/grafana/
/run.sh
