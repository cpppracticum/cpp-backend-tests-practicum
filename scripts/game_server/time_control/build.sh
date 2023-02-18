#!/bin/bash

BASE_DIR=${PWD}
SCRIPT_FOLDER=${BASE_DIR}/cpp-backend-tests-practicum/scripts/game_server/time_control
SOLUTION_FOLDER=${BASE_DIR}/game_server/solution/

docker build -t time_control $SOLUTION_FOLDER
