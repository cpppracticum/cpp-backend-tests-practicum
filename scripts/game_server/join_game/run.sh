#!/bin/bash

BASE_DIR=${PWD}
SCRIPT_FOLDER=${BASE_DIR}/cpp-backend-tests-practicum/scripts/game_server/join_game
SOLUTION_FOLDER=${BASE_DIR}/game_server/solution/

bash $SCRIPT_FOLDER/build.sh

export CONFIG_PATH=$SOLUTION_FOLDER/data/config.json
export IMAGE_NAME=join_game

pytest --workers=auto --junitxml=${BASE_DIR}/join_game.xml cpp-backend-tests-practicum/tests/test_s02_join_game.py
