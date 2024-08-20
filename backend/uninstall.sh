#!/bin/bash

sudo curl -sSL https://install.python-poetry.org > install-poetry.py
python3 install-poetry.py --uninstall
sudo curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py > get-poetry.py
python3 get-poetry.py --uninstall