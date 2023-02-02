#!/bin/bash

REPO=${PWD}

source ${REPO}/.venv/bin/activate

export DELIVERY_APP=${REPO}/sprint1/problems/map_json/solution/build/bin/game_server
export CONFIG_PATH=${REPO}/sprint1/problems/map_json/solution/data/config.json
export COMMAND_RUN="${DELIVERY_APP} ${CONFIG_PATH}"

python3 -m pytest --rootdir=${REPO} --verbose --junitxml=results.xml cpp-backend-tests-practicum/tests/test_l04_map_json.py
