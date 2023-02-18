#!/bin/bash

BASE_DIR=${PWD}
SCRIPT_FOLDER=${BASE_DIR}/cpp-backend-tests-practicum/scripts/game_server/find_return
SOLUTION_FOLDER=${BASE_DIR}/game_server/solution/

bash $SCRIPT_FOLDER/build.sh

export CONFIG_PATH=$SOLUTION_FOLDER/data/config.json
export IMAGE_NAME=find_return
export ENTRYPOINT='/app/game_server'
export CONTAINER_ARGS='--config-file /app/data/config.json --www-root /app/static/'

pytest --workers auto --junitxml=${BASE_DIR}/find_return.xml cpp-backend-tests-practicum/tests/test_s03_find_return.py
