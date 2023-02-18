#!/bin/bash

BASE_DIR=${PWD}
SCRIPT_FOLDER=${BASE_DIR}/cpp-backend-tests-practicum/scripts/game_server/leave_game
SOLUTION_FOLDER=${BASE_DIR}/game_server/solution/

docker build -t leave_game $SOLUTION_FOLDER
