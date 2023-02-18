#!/bin/bash

REPO=${PWD}

export CONFIG_PATH=${REPO}/sprint2/problems/command_line/solution/data/config.json
export IMAGE_NAME='command_line'
export ENTRYPOINT='/app/game_server'
export CONTAINER_ARGS='--config-file /app/data/config.json --www-root /app/static/'

pytest --workers auto --junitxml=${REPO}/command_line.xml cpp-backend-tests-practicum/tests/test_s02_command_line.py
