#!/bin/bash

function real_dir() {
  pushd "$1" >/dev/null
  pwd -P
  popd >/dev/null
}
SCRIPT_FOLDER=$(real_dir "$(dirname "$0")")

BASE_DIR=${SCRIPT_FOLDER}/../../../../
SOLUTION_FOLDER=${BASE_DIR}/sprint1/problems/sum/solution

source ${BASE_DIR}/.venv/bin/activate

cd ${SOLUTION_FOLDER} || exit 1
mkdir -p build
cd build
cmake ..
cmake --build . -j $(nproc)
