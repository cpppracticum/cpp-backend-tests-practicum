#!/bin/bash

function real_dir() {
  pushd "$1" >/dev/null
  pwd -P
  popd >/dev/null
}
SCRIPT_FOLDER=$(real_dir "$(dirname "$0")")

SPRINT=sprint3
TASK_NAME=game_state

BASE_DIR=${SCRIPT_FOLDER}/../../../../
TESTS_FOLDER=${BASE_DIR}/cpp-backend-tests-practicum/tests

SOLUTION_FOLDER=${BASE_DIR}/sprint3/problems/scores/solution

bash ${SCRIPT_FOLDER}/build.sh || exit 1

source ${BASE_DIR}/.venv/bin/activate

export CONFIG_PATH=${SOLUTION_FOLDER}/data/config.json
export IMAGE_NAME=scores
export ENTRYPOINT=/app/game_server
export CONTAINER_ARGS='--config-file /app/data/config.json --www-root /app/static/'
export JSON_SCHEMA_PATH=${TESTS_FOLDER}/schemas/${SPRINT}/${TASK_NAME}.json

pytest --workers auto --junitxml=${BASE_DIR}/${TASK_NAME}.xml ${TESTS_FOLDER}/test_s03_scores.py
