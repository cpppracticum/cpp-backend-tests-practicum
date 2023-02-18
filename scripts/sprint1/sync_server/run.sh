#!/bin/bash

REPO=${PWD}

source ${REPO}/.venv/bin/activate

export COMMAND_RUN=${REPO}/sprint1/problems/sync_server/solution/build/bin/hello

python3 -m pytest --rootdir=${REPO} --verbose --junitxml=results.xml cpp-backend-tests-practicum/tests/test_l02_hello_beast.py
