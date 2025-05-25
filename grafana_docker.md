## Timeline of the container launch

1 -> Docker image build (Dockerfile)

2 -> Container start via Docker compose (Create container from buit image; Mount volumes)

3 -> Container runtime: run ´run_all.sh´ script
Script ends wiith /run.sh that is the default Grafana startup script that launches Grafana

4 -> Grafana Startup (grafana.ini is loaded from /etc/grafana/grafana.ini; Provisioning files are loaded; Mounts plugins from /var/lib/grafana/plugins; Grafana is now accesible on port 3000)
