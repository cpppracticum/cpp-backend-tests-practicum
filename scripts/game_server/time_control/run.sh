#!/bin/bash

BASE_DIR=${PWD}
SCRIPT_FOLDER=${BASE_DIR}/cpp-backend-tests-practicum/scripts/game_server/move_players
SOLUTION_FOLDER=${BASE_DIR}/game_server/solution/

bash $SCRIPT_FOLDER/build.sh

export CONFIG_PATH=$SOLUTION_FOLDER/data/config.json
export IMAGE_NAME=time_control


pytest --workers=auto --junitxml=${BASE_DIR}/time_control.xml --workers auto cpp-backend-tests-practicum/tests/test_s02_time_control.py
