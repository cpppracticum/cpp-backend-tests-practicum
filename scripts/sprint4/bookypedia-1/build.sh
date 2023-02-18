#!/bin/bash

BASE_DIR=${PWD}
SCRIPT_FOLDER=${REPO}//cpp-backend-tests-practicum/scripts/sprint4/bookypedia-1

cd sprint4/problems/bookypedia-1/solution || exit 1
mkdir build
cd build
conan install .. --build=missing -s compiler.libcxx=libstdc++11 -s build_type=Release
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build .

cd $BASE_DIR

cp sprint4/problems/bookypedia-1/solution/build/bookypedia cpp-backend-tests-practicum/scripts/sprint4/bookypedia-1/bookypedia
cp cpp-backend-tests-practicum/tests/test_s04_bookypedia-1.py cpp-backend-tests-practicum/scripts/sprint4/bookypedia-1/test_s04_bookypedia-1.py

docker build -t bookypedia-1 ./${SCRIPT_FOLDER}/