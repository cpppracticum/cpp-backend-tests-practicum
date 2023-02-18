#!/bin/bash

cp cpp-backend-tests-practicum/tests/cpp/test_s02_logger/main.cpp sprint2/problems/logger/solution/
cd sprint2/problems/logger/solution || exit 1
mkdir build
cd build
conan install ..
cmake ..
cmake --build . -j $(nproc)
