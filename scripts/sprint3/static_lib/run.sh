#!/bin/bash

REPO=${PWD}

export CONFIG_PATH=${REPO}/sprint3/problems/static_lib/solution/data/config.json
export IMAGE_NAME='static_lib'
export ENTRYPOINT='/app/game_server'
export CONTAINER_ARGS='--config-file /app/data/config.json --www-root /app/static/'

pytest --workers auto --junitxml=${REPO}/static_lib.xml cpp-backend-tests-practicum/tests/test_s03_gen_objects.py
