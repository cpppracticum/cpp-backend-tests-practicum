#!/bin/bash

BASE_DIR=${PWD}
SCRIPT_FOLDER=${BASE_DIR}/cpp-backend-tests-practicum/scripts/game_server/map_json
SOLUTION_FOLDER=${BASE_DIR}/game_server/solution/

cp -r $SOLUTION_FOLDER $SCRIPT_FOLDER
rm -r $SCRIPT_FOLDER/solution/build
docker build -t map_json $SCRIPT_FOLDER
