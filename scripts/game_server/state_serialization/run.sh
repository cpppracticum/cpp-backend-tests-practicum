#!/bin/bash

BASE_DIR=${PWD}
SCRIPT_FOLDER=${BASE_DIR}/cpp-backend-tests-practicum/scripts/game_server/state_serialization
SOLUTION_FOLDER=${BASE_DIR}/game_server/solution/

bash $SCRIPT_FOLDER/build.sh

export CONFIG_PATH=$SOLUTION_FOLDER/data/config.json

export VOLUME_PATH=$SCRIPT_FOLDER/volume
export IMAGE_NAME=state_serialization

pytest --junitxml=${BASE_DIR}/state_serialization.xml cpp-backend-tests-practicum/tests/test_s04_state_serialization.py

rm -r $SCRIPT_FOLDER/volume