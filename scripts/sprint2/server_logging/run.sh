#!/bin/bash

function real_dir() {
  pushd "$1" >/dev/null
  pwd -P
  popd >/dev/null
}
SCRIPT_FOLDER=$(real_dir "$(dirname "$0")")

BASE_DIR=${SCRIPT_FOLDER}/../../../../
SOLUTION_FOLDER=${BASE_DIR}/sprint2/problems/server_logging/solution

bash ${SCRIPT_FOLDER}/build.sh

export CONFIG_PATH=${SOLUTION_FOLDER}/data/config.json
export IMAGE_NAME=server_logging

pytest --workers auto --junitxml=${BASE_DIR}/server_logging.xml ${BASE_DIR}/cpp-backend-tests-practicum/tests/test_s02_server_logging.py