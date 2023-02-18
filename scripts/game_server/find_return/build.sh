#!/bin/bash

BASE_DIR=${PWD}
SCRIPT_FOLDER=${BASE_DIR}/cpp-backend-tests-practicum/scripts/game_server/find_return
SOLUTION_FOLDER=${BASE_DIR}/game_server/solution/

docker build -t find_return $SOLUTION_FOLDER
