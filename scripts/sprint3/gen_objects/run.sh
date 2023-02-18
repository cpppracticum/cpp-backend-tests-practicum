#!/bin/bash

REPO=${PWD}

export CONFIG_PATH=${REPO}/sprint3/problems/gen_objects/solution/data/config.json
export IMAGE_NAME='gen_objects'
export ENTRYPOINT='/app/game_server'
export CONTAINER_ARGS='--config-file /app/data/config.json --www-root /app/static/'

pytest --workers auto --junitxml=${REPO}/gen_objects.xml cpp-backend-tests-practicum/tests/test_s03_gen_objects.py
