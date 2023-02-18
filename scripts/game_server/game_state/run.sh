#!/bin/bash


BASE_DIR=${PWD}
SCRIPT_FOLDER=${BASE_DIR}/cpp-backend-tests-practicum/scripts/game_server/game_state
SOLUTION_FOLDER=${BASE_DIR}/game_server/solution/

bash $SCRIPT_FOLDER/build.sh

export CONFIG_PATH=$SOLUTION_FOLDER/data/config.json
export IMAGE_NAME=game_state

pytest --workers auto --junitxml=${BASE_DIR}/game_state.xml cpp-backend-tests-practicum/tests/test_s02_game_state.py
