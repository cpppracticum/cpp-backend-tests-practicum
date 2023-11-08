#!/bin/bash

function real_dir() {
  pushd "$1" >/dev/null
  pwd -P
  popd >/dev/null
}
SCRIPT_FOLDER=$(real_dir "$(dirname "$0")")

BASE_DIR=${SCRIPT_FOLDER}/../../../../
SOLUTION_FOLDER=${BASE_DIR}/sprint1/problems/sum/solution

bash ${SCRIPT_FOLDER}/build.sh || exit 1

source ${BASE_DIR}/.venv/bin/activate

A=$((1 + $RANDOM % 10))
B=$((1 + $RANDOM % 10))
C=$(($A + $B))

answer=$(echo ${A} ${B} | ${SOLUTION_FOLDER}/build/sum)



if [ "$answer" != ${C} ]; then
  exit 1
fi
