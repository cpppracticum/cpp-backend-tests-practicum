#!/bin/bash

BASE_DIR=${PWD}
SCRIPT_FOLDER=${BASE_DIR}/cpp-backend-tests-practicum/scripts/game_server/map_json
SOLUTION_FOLDER=${BASE_DIR}/game_server/solution/

export IMAGE_NAME=final_task
python3 -m pytest --workers=auto --rootdir=${BASE_DIR} --verbose --junitxml=results.xml cpp-backend-tests-practicum/tests/test_l05_final_task.py
