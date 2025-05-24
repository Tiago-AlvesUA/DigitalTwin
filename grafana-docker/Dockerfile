FROM grafana/grafana:10.3.1-ubuntu

USER 0

# Install Node.js and Yarn (using Nodesource instead of `n`, which doesn't work reliably in Docker)
# RUN apt update && \
#     apt install -y curl gnupg && \
#     curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
#     apt install -y nodejs yarn

RUN apt update && apt install -y npm && npm install -g yarn
RUN npm install -g n && n 18


#
ENV GF_PATHS_CONFIG=/etc/grafana/grafana.ini
COPY grafana.ini /etc/grafana/grafana.ini

COPY plugins /var/lib/grafana/plugins
# RUN chown -R 472:472 /var/lib/grafana/plugins
# JÁ DEI PERMISSÕES 472 AO FICHEIRO PLUGINS NO MEU PC, ANTES DE PASSAR PARA O DOCKER
# USER 472
# WORKDIR /var/lib/grafana/plugins/grafana-app-opentwins/src
# RUN yarn install

WORKDIR /usr/share/grafana
COPY run_all.sh .
#RUN chmod +x run_all.sh

ENTRYPOINT ["./run_all.sh"]
