#!/bin/bash

REPO=${PWD}

export CONFIG_PATH=${REPO}/sprint3/problems/find_return/solution/data/config.json
export IMAGE_NAME='find_return'
export ENTRYPOINT='/app/game_server'
export CONTAINER_ARGS='--config-file /app/data/config.json --www-root /app/static/'

pytest --workers auto --junitxml=${REPO}/find_return.xml cpp-backend-tests-practicum/tests/test_s03_find_return.py
