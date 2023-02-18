#!/bin/bash

REPO=${PWD}

source ${REPO}/.venv/bin/activate

export CONFIG_PATH=${REPO}/sprint2/problems/server_logging/solution/data/config.json
export IMAGE_NAME='server_logging'

pytest --workers auto --junitxml=${REPO}/server_logging.xml cpp-backend-tests-practicum/tests/test_s02_server_logging.py
