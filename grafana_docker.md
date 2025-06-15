## Timeline of the container launch

1 -> Docker image build (Dockerfile)

2 -> Container start via Docker compose (Create container from buit image; Mount volumes (volumes are not used for now))

3 -> Container runtime: run ´run_all.sh´ script
Script ends wiith /run.sh that is the default Grafana startup script that launches Grafana

( REVISE THIS POINT )
4 -> Grafana Startup (grafana.ini is loaded from /etc/grafana/grafana.ini;  Grafana is now accesible on port 3000)


## Structure and explanation

- Dockerfile, docker-compose (with only the grafana service), grafana.ini and run_all.sh at the root folder.

- Plugins folder contains the open twins app. 
    - This plugin is copied to /var/lib/grafana/plugins of the container (by instructions at the dockerfile)

- templates folder contain both ditto dashboard and eclipse ditto datasource as json files.
    - These are both instantiated by the run_all script, using environment variables too.

