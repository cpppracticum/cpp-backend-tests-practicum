#!/bin/bash

BASE_DIR=${PWD}
SCRIPT_FOLDER=${BASE_DIR}/cpp-backend-tests-practicum/scripts/game_server/server_logging
SOLUTION_FOLDER=${BASE_DIR}/game_server/solution/

bash $SCRIPT_FOLDER/build.sh

export CONFIG_PATH=$SCRIPT_FOLDER/data/config.json
export IMAGE_NAME=server_logging

pytest --workers auto --junitxml=${BASE_DIR}/server_logging.xml cpp-backend-tests-practicum/tests/test_s02_server_logging.py
