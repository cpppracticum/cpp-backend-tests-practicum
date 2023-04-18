#!/bin/bash

function real_dir() {
  pushd "$1" >/dev/null
  pwd -P
  popd >/dev/null
}
SCRIPT_FOLDER=$(real_dir "$(dirname "$0")")

SPRINT=sprint1
TASK_NAME=final_task

BASE_DIR=${SCRIPT_FOLDER}/../../../..
TESTS_FOLDER=${BASE_DIR}/cpp-backend-tests-practicum/tests

SOLUTION_FOLDER=${BASE_DIR}/sprint1/problems/final_task/solution

bash ${SCRIPT_FOLDER}/build.sh || exit 1

source ${BASE_DIR}/.venv/bin/activate

export IMAGE_NAME=final_task
export CONFIG_PATH=${SOLUTION_FOLDER}/data/config.json
export JSON_SCHEMA_PATH=${TESTS_FOLDER}/schemas/${SPRINT}/${TASK_NAME}

python3 -m pytest --workers=auto --rootdir=${BASE_DIR} --verbose --junitxml=${BASE_DIR}/${TASK_NAME}.xml ${TESTS_FOLDER}/test_l05_final_task.py
