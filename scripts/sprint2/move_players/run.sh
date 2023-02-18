#!/bin/bash

REPO=${PWD}

export CONFIG_PATH=${REPO}/sprint2/problems/move_players/solution/data/config.json
export IMAGE_NAME='move_players'

pytest --workers auto --junitxml=${REPO}/move_players.xml cpp-backend-tests-practicum/tests/test_s02_move_players.py