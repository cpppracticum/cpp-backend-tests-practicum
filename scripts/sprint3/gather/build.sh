#!/bin/bash

cp cpp-backend-tests-practicum/tests/cpp/test_s03_gather/* sprint3/problems/gather/solution/tests/
cd sprint3/problems/gather/solution || exit 1
docker build -t gather .
