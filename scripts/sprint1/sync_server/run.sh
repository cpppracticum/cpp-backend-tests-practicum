#!/bin/bash

REPO=${PWD}

source ${REPO}/.venv/bin/activate

export DELIVERY_APP=${REPO}/sprint1/problems/sync_server/solution/build/bin/hello
export COMMAND_RUN=${DELIVERY_APP}

python3 -m pytest --rootdir=${REPO} --verbose --junitxml=results.xml cpp-backend-tests-practicum/tests/test_l02_hello_beast.py
