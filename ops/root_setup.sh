#!/usr/bin/env bash

APP_HOME='/opt/learnterra'
APP_DIR="$APP_HOME/app"
VENV_DIR="$APP_HOME/venv"

yum install git python3 -y

git clone https://github.com/maludwig/bashrc /tmp/bashrc
/tmp/bashrc/install

useradd --home-dir "$APP_HOME" --create-home learnterra

# Setup app

APP_HOME='/opt/learnterra'
APP_DIR="$APP_HOME/app"
VENV_DIR="$APP_HOME/venv"

sudo git clone https://github.com/turiyag/learnterra.git "$APP_DIR"

sudo pip3 install ansible


sudo /usr/local/bin/ansible-playbook -vv "$APP_DIR/ops/ansible/r-learnterra.yml" -i "$APP_DIR/ops/ansible/inventory/localhost.yml"

sudo -u learnterra "$APP_DIR/ops/user_setup.sh"

# Setup gunicorn service
rsync -avi "$APP_DIR/ops/files/" "/"
systemctl enable gunicorn.socket
systemctl start gunicorn.socket

# Test gunicorn
curl --unix-socket /run/gunicorn/socket http