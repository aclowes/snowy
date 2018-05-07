#!/bin/bash

set -e

# clone if it doesn't exist
ls snowy || git clone https://github.com/aclowes/snowy.git

cd snowy
git pull

pip install -q --upgrade pip setuptools
pip install -q -r requirements.txt

mkdir -p data
python runner.py
