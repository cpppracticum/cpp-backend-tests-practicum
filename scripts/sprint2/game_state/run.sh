#!/bin/bash

REPO=${PWD}

export CONFIG_PATH=${REPO}/sprint2/problems/game_state/solution/data/config.json
export IMAGE_NAME='game_state'

pytest --workers auto --junitxml=${REPO}/game_state.xml cpp-backend-tests-practicum/tests/test_s02_game_state.py
