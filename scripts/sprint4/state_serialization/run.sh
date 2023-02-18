#!/bin/bash

REPO=${PWD}

export CONFIG_PATH=${REPO}/sprint4/problems/state_serialization/solution/data/config.json
export VOLUME_PATH=${REPO}/sprint4/problems/state_serialization/volume
export IMAGE_NAME='state_serialization'

pytest --junitxml=${REPO}/state_serialization.xml cpp-backend-tests-practicum/tests/test_s04_state_serialization.py
