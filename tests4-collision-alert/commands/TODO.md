## Collision alert delay

- MCM(OBU) -> MCM Reception at Agent -> Collision Check -> (Ditto Alert Received) -> Alert Received (WS OBU)
    - OBU->(Broker)->Agent : Feito com o generation delta time **NO CÓDIGO**        DONE no mqtt.py
    - MCM->Collision Check Done : Tirar os tempos time.time()
        - tempo em que MCM é recebida   **NO CÓDIGO**       DONE no mqtt.py
        - tempo em que a verificação colisão acaba  **NO CÓDIGO**       DONE no mqtt.py
    - Collision Check Done->Alerta Ditto : Tirar os tempos time.time()
        - tempo em que a verificação colisão acaba* **NO CÓDIGO**       DONE no mqtt.py
        - tempo em que live alert message chega ao ditto    **LOGS**        DONE nos logs do ditto gateway
    - Ditto->OBU(WS) : Tirar os tempos time.time()
        - tempo em que live alert message chega ao ditto*   **LOGS**        DONE nos logs do ditto gateway
        - tempo em que alerta chega à OBU pelo WS   **NO CÓDIGO**       DONE no alert-mec-obu.py


(*Tempos repetidos)
passo 0 - Dar reset ao Modem 5G sempre que possível (ao início parece que ele funciona bem, mas passado um tempo começa a dar disconnects)
passo 1 - Correr alert-mec-obu.py (tests/alert-mec-obu.py)
passo 2 - Correr Mjpeg Stream, Agente
passo 3 - Ir buscar os tempos todos guardados pelo mqtt.py, kubectl logs -n cloud2edge deployment/c2e-ditto-gateway | grep "Forwarding thing signal" | tail -n 1000 | jq -r '."@timestamp"' e results tempos obu-alert-reception-times.csv.


