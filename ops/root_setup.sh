#!/usr/bin/env bash

APP_HOME='/opt/learnterra'
APP_DIR="$APP_HOME/app"
VENV_DIR="$APP_HOME/venv"

function setup_app {
    yum install git python3 -y

    git clone https://github.com/maludwig/bashrc /tmp/bashrc
    /tmp/bashrc/install

    useradd --home-dir "$APP_HOME" --create-home learnterra

    # Setup app
    git clone https://github.com/turiyag/learnterra.git "$APP_DIR"

    pip3 install ansible
    /usr/local/bin/ansible-playbook -vvv "$APP_DIR/ops/ansible/r-learnterra.yml" -i "$APP_DIR/ops/ansible/inventory/localhost.yml"
}

setup_app | tee -a /var/log/setup_app.log


