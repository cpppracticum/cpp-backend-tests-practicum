#!/bin/bash

BASE_DIR=${PWD}
SCRIPT_FOLDER=${BASE_DIR}/cpp-backend-tests-practicum/scripts/game_server/move_players
SOLUTION_FOLDER=${BASE_DIR}/game_server/solution/

docker build -t move_players $SOLUTION_FOLDER
