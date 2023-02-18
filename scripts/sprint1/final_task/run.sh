#!/bin/bash

REPO=${PWD}

source ${REPO}/.venv/bin/activate

export IMAGE_NAME="final_task"
python3 -m pytest --workers=auto --rootdir=${REPO} --verbose --junitxml=results.xml cpp-backend-tests-practicum/tests/test_l05_final_task.py
