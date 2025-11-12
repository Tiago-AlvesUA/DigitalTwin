## How to run all

- First start 5G connection

- Then build/run
    - In the local-twin:
        > create venv / activate venv
        > python3 local-twin.py
    - In the data-collector:
        > cd build
        > cmake ..
        > make
        > sudo ./src/it2s-data-reader
    - In the loggings:
        > create venv / activate venv
        > python3 network-delay.py
        > python3 network-tt.py