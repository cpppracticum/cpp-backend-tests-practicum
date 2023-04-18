#!/bin/bash

function real_dir() {
  pushd "$1" >/dev/null
  pwd -P
  popd >/dev/null
}
SCRIPT_FOLDER=$(real_dir "$(dirname "$0")")

SPRINT=sprint1
TASK_NAME=map_json

BASE_DIR=${SCRIPT_FOLDER}/../../../../
TESTS_FOLDER=${BASE_DIR}/cpp-backend-tests-practicum/tests

SOLUTION_FOLDER=${BASE_DIR}/${SPRINT}/problems/${TASK_NAME}/solution

bash ${SCRIPT_FOLDER}/build.sh || exit 1

source ${BASE_DIR}/.venv/bin/activate

export DELIVERY_APP=${SOLUTION_FOLDER}/build/bin/game_server
export CONFIG_PATH=${SOLUTION_FOLDER}/data/config.json
export COMMAND_RUN="${DELIVERY_APP} ${CONFIG_PATH}"

export JSON_SCHEMA_PATH=${TESTS_FOLDER}/schemas/${SPRINT}/${TASK_NAME}.json

python3 -m pytest --rootdir=${BASE_DIR} --verbose --junitxml=${BASE_DIR}/${TASK_NAME}.xml ${TESTS_FOLDER}/test_l04_map_json.py
