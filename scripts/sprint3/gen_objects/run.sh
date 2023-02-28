#!/bin/bash

function real_dir() {
  pushd "$1" >/dev/null
  pwd -P
  popd >/dev/null
}
SCRIPT_FOLDER=$(real_dir "$(dirname "$0")")

BASE_DIR=${SCRIPT_FOLDER}/../../../../
SOLUTION_FOLDER=${BASE_DIR}/sprint3/problems/gen_objects/solution
SCRIPT_FOLDER=${BASE_DIR}/cpp-backend-tests-practicum/scripts/sprint3/gen_objects

bash ${SCRIPT_FOLDER}/build.sh

export CONFIG_PATH=${SOLUTION_FOLDER}/data/config.json
export IMAGE_NAME=gen_objects
export ENTRYPOINT=/app/game_server
export CONTAINER_ARGS='--config-file /app/data/config.json --www-root /app/static/'

pytest --workers auto --junitxml=${BASE_DIR}/gen_objects.xml ${BASE_DIR}/cpp-backend-tests-practicum/tests/test_s03_gen_objects.py