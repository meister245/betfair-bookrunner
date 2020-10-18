#!/usr/bin/env bash

sudo apt update;

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )";
TOP_DIR="$( realpath $CURRENT_DIR/../ )";

# setup venv
sudo apt install python3 python3-dev python3-setuptools python3-venv --yes;

PYTHON_PATH="/usr/bin/env python3";
$PYTHON_PATH -m pip install --upgrade pip setuptools wheel;

rm -rf $TOP_DIR/venv;
$PYTHON_PATH -m venv $TOP_DIR/venv;

PYTHON_VENV_PATH="$TOP_DIR/venv/bin/python3";
$PYTHON_VENV_PATH -m pip install --upgrade pip setuptools wheel;
$PYTHON_VENV_PATH -m pip install -r $TOP_DIR/requirements-dev.txt;
