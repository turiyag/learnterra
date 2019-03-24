#!/usr/bin/env bash

APP_DIR="$HOME/app"
VENV_DIR="$HOME/venv"

python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install -r "$APP_DIR/requirements.txt"

