## Configuration of the Agent

Before running the agent, a virtual environment must be created and the packages from requirements.txt must be installed via pip.
The package pyquadkey2 requires Python C headers to be installed as it is a small C extension. 
Consequently, the following three commands are necessary to setup the agent: 

`sudo apt install -y python3.10-dev build-essential`
`python3 -m venv venv`
`pip install -r requirements.txt`