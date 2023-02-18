#!/bin/bash

BASE_DIR=${PWD}
SCRIPT_FOLDER=${BASE_DIR}/cpp-backend-tests-practicum/scripts/sprint4/leave_game
SOLUTION_FOLDER=sprint4/problems/leave_game/solution

docker build -t leave_game ./${SOLUTION_FOLDER}/
