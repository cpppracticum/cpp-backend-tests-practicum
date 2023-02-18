#!/bin/bash

BASE_DIR=${PWD}
SCRIPT_FOLDER=${BASE_DIR}/cpp-backend-tests-practicum/scripts/game_server/game_state
SOLUTION_FOLDER=${BASE_DIR}/game_server/solution/

docker build -t game_state $SOLUTION_FOLDER
