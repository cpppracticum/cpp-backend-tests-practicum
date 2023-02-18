#!/bin/bash

BASE_DIR=${PWD}
SCRIPT_FOLDER=${BASE_DIR}/cpp-backend-tests-practicum/scripts/game_server/state_serialization
SOLUTION_FOLDER=${BASE_DIR}/game_server/solution/

docker build -t state_serialization $SOLUTION_FOLDER

mkdir -p $SCRIPT_FOLDER/volume
chmod 777 $SCRIPT_FOLDER/volume
