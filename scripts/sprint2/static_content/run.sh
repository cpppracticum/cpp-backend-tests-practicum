#!/bin/bash

REPO=${PWD}

source ${REPO}/.venv/bin/activate

export DELIVERY_APP=${REPO}/sprint2/problems/static_content/solution/build/bin/game_server
export CONFIG_PATH=${REPO}/sprint2/problems/static_content/solution/data/config.json
export DATA_PATH=${REPO}/sprint2/problems/static_content/solution/static/

export COMMAND_RUN="${DELIVERY_APP} ${CONFIG_PATH} ${DATA_PATH}"

python3 -m pytest --rootdir=${REPO} --verbose --junitxml=results.xml cpp-backend-tests-practicum/tests/test_s02_static_content.py
