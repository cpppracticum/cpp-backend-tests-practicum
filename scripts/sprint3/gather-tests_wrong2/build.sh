#!/bin/bash

cp -r cpp-backend-tests-practicum/tests/cpp/test_s03_gather-tests/* sprint3/problems/gather-tests/solution/src/
cp cpp-backend-tests-practicum/tests/cpp/test_s03_gather-tests/wrong/collision_detector.cpp sprint3/problems/gather-tests/solution/src/
cp cpp-backend-tests-practicum/tests/cpp/test_s03_gather-tests/wrong/CMakeLists.txt sprint3/problems/gather-tests/solution/
cp cpp-backend-tests-practicum/tests/cpp/test_s03_gather-tests/wrong/Dockerfile2 sprint3/problems/gather-tests/solution/Dockerfile
cd sprint3/problems/gather-tests/solution || exit 1
docker build -t gather-tests_wrong2 .
