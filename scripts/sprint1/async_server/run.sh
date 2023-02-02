#!/bin/bash

REPO=${PWD}

source ${REPO}/.venv/bin/activate

export DELIVERY_APP=${REPO}/sprint1/problems/async_server/solution/build/bin/hello_async
export COMMAND_RUN=${DELIVERY_APP}

python3 -m pytest --rootdir=${REPO} --verbose --junitxml=results.xml cpp-backend-tests-practicum/tests/test_l03_hello_async.py
