#!/bin/bash

python -m  venv .venv   
source .venv/bin/activate    
mkdir gpsPositionsv2
pip install -r requirements.txt
isort *.py
black --line-length 120 *.py
python main.py --skip-zero-delay
deactivate