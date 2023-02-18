#!/bin/bash

BASE_DIR=${PWD}
SCRIPT_FOLDER=${BASE_DIR}/cpp-backend-tests-practicum/scripts/game_server/move_players
SOLUTION_FOLDER=${BASE_DIR}/game_server/solution/

bash $SCRIPT_FOLDER/build.sh

export IMAGE_NAME=move_players

pytest --workers auto --junitxml=${BASE_DIR}/move_players.xml cpp-backend-tests-practicum/tests/test_s02_move_players.py