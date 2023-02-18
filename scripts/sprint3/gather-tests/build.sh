#!/bin/bash

cp -r cpp-backend-tests-practicum/tests/cpp/test_s03_gather-tests/* sprint3/problems/gather-tests/solution/src/
cd sprint3/problems/gather-tests/solution || exit 1
docker build -t gather-tests .
