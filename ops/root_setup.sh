#!/usr/bin/env bash

APP_HOME='/opt/learnterra'
APP_DIR="$APP_HOME/app"
VENV_DIR="$APP_HOME/venv"

function setup_app {
    yum install git python3 -y

    if [[ -d /etc/bashrc.extensions ]]; then
        git clone https://github.com/maludwig/bashrc /tmp/bashrc
        /tmp/bashrc/install
    fi

    if [[ -d "$APP_HOME" ]]; then
        useradd --home-dir "$APP_HOME" --create-home learnterra
    fi

    # Setup app
    if [[ -d "$APP_DIR" ]]; then
        git clone https://github.com/turiyag/learnterra.git "$APP_DIR"
    fi
    cd "$APP_DIR"
    git pull origin master

    if ! which ansible-playbook; then
        pip3 install ansible
    fi
    ansible-playbook -vvv "$APP_DIR/ops/ansible/r-learnterra.yml" -i "$APP_DIR/ops/ansible/inventory/localhost.yml"
}

setup_app | tee -a /var/log/setup_app.log


