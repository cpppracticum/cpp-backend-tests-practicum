#!/bin/bash

BASE_DIR=${PWD}
SCRIPT_FOLDER=${REPO}//cpp-backend-tests-practicum/scripts/sprint4/bookypedia-2

cd sprint4/problems/bookypedia-2/solution || exit 1
mkdir build
cd build
conan install ..
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build .

cd $BASE_DIR

cp sprint4/problems/bookypedia-2/solution/build/bookypedia cpp-backend-tests-practicum/scripts/sprint4/bookypedia-2/bookypedia
cp cpp-backend-tests-practicum/tests/test_s04_bookypedia-2.py cpp-backend-tests-practicum/scripts/sprint4/bookypedia-2/test_s04_bookypedia-2.py

docker build -t bookypedia-2 ./${SCRIPT_FOLDER}/