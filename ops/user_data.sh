#!/usr/bin/env bash

APP_HOME='/opt/learnterra'
APP_DIR="$APP_HOME/app"
VENV_DIR="$APP_HOME/venv"

yum install git python3 -y
useradd --home-dir "$APP_HOME" --create-home learnterra
git clone https://github.com/turiyag/learnterra.git "$APP_DIR"

cd "$APP_DIR"
./ops/root_setup.sh
