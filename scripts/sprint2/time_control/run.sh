#!/bin/bash

REPO=${PWD}

export CONFIG_PATH=${REPO}/sprint2/problems/time_control/solution/data/config.json
export IMAGE_NAME='time_control'


pytest --junitxml=${REPO}/time_control.xml --workers auto cpp-backend-tests-practicum/tests/test_s02_time_control.py
