#!/bin/bash

REPO=${PWD}

export REPORT_PATH=${REPO}/sprint3/problems/instrumentation/solution/report
export BINARY_PATH=${REPO}/sprint3/problems/instrumentation/solution/event2dot
export ARG=${REPO}/sprint3/problems/instrumentation/solution/inputs

pytest --junitxml=${REPO}/instrumentation.xml cpp-backend-tests-practicum/tests/test_s03_instrumentation.py
