#!/usr/bin/env bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )";
TOP_DIR="$( realpath $CURRENT_DIR/../ )";

[ ! -d "$TOP_DIR/venv" ] && $TOP_DIR/scripts/setup_venv.sh

PYTHON_VENV_PATH="$TOP_DIR/venv/bin/python3";

$PYTHON_VENV_PATH $TOP_DIR/app/service.py "$@"
