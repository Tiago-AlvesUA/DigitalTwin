## Collision alert delay

Three folders are necessary to create, in order to store time checkpoints, time interval results, and charts.

### Time intervals measured

- **OBU -> Agent**: 
    - Obter generation delta time que vai nas MCMs e subtrair este tempo a um `time.time()` quando esta mensagem é recebida no agente; (Feito no código: `mqtt.py`; subtração dos tempos já feita também)
- **Collision Checking Process**:
    - Desde: `time.time()` quando MCM é recebida; (Feito no código: `mqtt.py`)
    - Até: `time.time()` quando a verificação de colisão acaba; (Feito no código: `mqtt.py`)
- **Alert -> Ditto**:
    - Desde: `time.time()` quando a verificação de colisão acaba; (Igual acima)
    - Até: `timestamp` quando alert message chega ao Ditto; (Obtido nos logs do c2e-ditto-gateway)
- **Ditto -> OBU(WS)**:
    - Desde: `timestamp` quando alert message chega ao Ditto; (Igual acima)
    - Até: tempo em que alerta chega à OBU pelo WebSocket. (Feito no código: `alert-mec-obu.py`)
- **E2E Total Delay**

![alt text](image1.png)


### Obtaining time checkpoints

1. Dar reset ao Modem 5G sempre que possível (ao início parece que ele funciona bem, mas passado um tempo começa a dar disconnects)

2. Correr *alert-mec-obu.py* (tests/alert-mec-obu.py), na OBU, para 10020 samples

3. Correr *mjpeg_stream.py*, no Agente

4. Correr *agent.py*, no Agente, para 10020 samples de MCMs

    **ESPERAR**

5. Ir buscar os tempos todos guardados pelo worker mqtt.py (em results: mcm-reception-delays.csv, mcm-reception-times.csv, check-collision-done-times.csv), e os logs do c2e-ditto-gateway das últimas 10020 mensagens, no Agente:
    - Results do worker mqtt:
        - `scp mcm-reception-delays.csv talves@172.16.10.27:~/Documentos/bolsa/DigitalTwin/tests4-collision-alert/PdA_10000messages/results` (already a **result**)
        - `scp mcm-reception-times.csv talves@172.16.10.27:~/Documentos/bolsa/DigitalTwin/tests4-collision-alert/PdA_10000messages/checkpoints`
        - `scp check-collision-done-times.csv talves@172.16.10.27:~/Documentos/bolsa/DigitalTwin/tests4-collision-alert/PdA_10000messages/checkpoints`
    - Logs:
        - `kubectl logs -n cloud2edge deployment/c2e-ditto-gateway | grep "messages.commands:thingMessage" | tail -n 10020 | jq -r '."@timestamp"' > ditto-receive-times.txt`
        - `scp ditto-receive-times.txt talves@172.16.10.27:~/Documentos/bolsa/DigitalTwin/tests4-collision-alert/PdA_10000messages/checkpoints`

6. Ir buscar results tempos guardados pelo alert-mec-obu.py, na OBU (results: obu-alert-reception-times.txt).
    - `scp obu-alert-reception-times.txt talves@172.16.10.27:~/Documentos/bolsa/DigitalTwin/tests4-collision-alert/PdA_10000messages/checkpoints`

### Calculating time intervals (results)

1. (*mcm-reception-delays.csv* already obtained)
2. Correr `collision-check-delay.py` para obter *collision-check-delays.csv*
3. Correr `checkColl-to-ditto-delay.py` para obter *checkcoll-to-ditto-delays.csv*
4. Correr `ditto-to-OBU-delay.py` para obter *ditto-to-ws-delays.csv*
5. Correr `SUM_ALL.py` para obter *total-delays.csv*

### Generating the charts

- `multiple-boxplot.py`
- `multiple-cdf.py`
- `one-stacked-bar-chart.py`
- `stacked-bar-chart.py`

---

**NOTA:** Para deixar apenas a mensagem de log relevante (Forwarding thing signal with ID org.acme:vehicle and type messages.commands:thingMessage to 'things' shard region), no Ditto Services Logging deixa-se apenas o logger *org.eclipse.ditto.edge.service.dispatching* a emitir info:
![alt text](image2.png)

---