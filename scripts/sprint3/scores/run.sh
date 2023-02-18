#!/bin/bash

REPO=${PWD}

export CONFIG_PATH=${REPO}/sprint3/problems/scores/solution/data/config.json
export IMAGE_NAME='scores'
export ENTRYPOINT='/app/game_server'
export CONTAINER_ARGS='--config-file /app/data/config.json --www-root /app/static/'

pytest --workers auto --junitxml=${REPO}/scores.xml cpp-backend-tests-practicum/tests/test_s03_scores.py
