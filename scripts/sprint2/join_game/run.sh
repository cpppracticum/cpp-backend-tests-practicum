#!/bin/bash

REPO=${PWD}

export CONFIG_PATH=${REPO}/sprint2/problems/join_game/solution/data/config.json
export IMAGE_NAME='join_game'

pytest --workers auto --junitxml=${REPO}/join_game.xml cpp-backend-tests-practicum/tests/test_s02_join_game.py
