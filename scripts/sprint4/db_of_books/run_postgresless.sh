#!/bin/bash

function real_dir() {
  pushd "$1" >/dev/null
  pwd -P
  popd >/dev/null
}
SCRIPT_FOLDER=$(real_dir "$(dirname "$0")")

BASE_DIR=${SCRIPT_FOLDER}/../../../../
SOLUTION_FOLDER=${BASE_DIR}/sprint4/problems/db_of_books/solution
GET_IP=${SCRIPT_FOLDER}/../get_ip.py

bash $SCRIPT_FOLDER/build.sh || exit 1

source ${BASE_DIR}/.venv/bin/activate

export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=Mys3Cr3t
export POSTGRES_HOST=postgres
export POSTGRES_PORT=5432

export DELIVERY_APP=${SOLUTION_FOLDER}/build/book_manager

python3 ${BASE_DIR}/cpp-backend-tests-practicum/tests/test_s04_db_of_books.py

pytest --junitxml=${BASE_DIR}/db_of_books.xml ${BASE_DIR}/cpp-backend-tests-practicum/tests/test_s04_db_of_books.py
