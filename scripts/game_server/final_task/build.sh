#!/bin/bash

BASE_DIR=${PWD}
SCRIPT_FOLDER=${BASE_DIR}/cpp-backend-tests-practicum/scripts/game_server/final_task
SOLUTION_FOLDER=${BASE_DIR}/game_server/solution/

cd $SOLUTION_FOLDER || exit 1

docker build -t final_task .
