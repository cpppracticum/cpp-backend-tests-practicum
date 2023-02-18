#!/bin/bash

BASE_DIR=${PWD}
SCRIPT_FOLDER=${BASE_DIR}/cpp-backend-tests-practicum/scripts/game_server/static_content
SOLUTION_FOLDER=${BASE_DIR}/game_server/solution/

bash $SCRIPT_FOLDER/build.sh

export IMAGE_NAME=static_content

python3 -m pytest --workers=auto --rootdir=${BASE_DIR} --verbose --junitxml=results.xml cpp-backend-tests-practicum/tests/test_s02_static_content.py


rm -r $SCRIPT_FOLDER/solution