#!/usr/bin/env bash

APP_HOME='/opt/learnterra'
APP_DIR="$APP_HOME/app"
VENV_DIR="$APP_HOME/venv"

yum install git python3 -y

git clone https://github.com/maludwig/bashrc /tmp/bashrc
/tmp/bashrc/install

useradd --home-dir "$APP_HOME" --create-home learnterra

# Setup app
git clone https://github.com/turiyag/learnterra.git "$APP_DIR"
sudo -u learnterra "$APP_DIR/ops/user_setup.sh"

# Setup gunicorn service
rsync -avi "$APP_DIR/ops/files/" "/"
systemctl enable gunicorn.socket
systemctl start gunicorn.socket
