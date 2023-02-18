#!/bin/bash

BASE_DIR=${PWD}
SCRIPT_FOLDER=${BASE_DIR}/cpp-backend-tests-practicum/scripts/game_server/leave_game
SOLUTION_FOLDER=${BASE_DIR}/game_server/solution/
GET_IP=${SCRIPT_FOLDER}/get_ip.py

bash $SCRIPT_FOLDER/build.sh

docker container stop postgres
docker container rm postgres
POSTGRES_ID=$(docker run --name postgres -e POSTGRES_HOST_AUTH_METHOD=trust -d --rm postgres)

sleep 5s # wait while postgres is setting up

export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=Mys3Cr3t
export POSTGRES_HOST=$(python3 ${GET_IP} $POSTGRES_ID)
export POSTGRES_PORT=5432
export IMAGE_NAME=leave_game
export CONFIG_PATH=$SOLUTION_FOLDER/data/config.json

pytest --workers 4 --junitxml=leave_game.xml cpp-backend-tests-practicum/tests/test_s04_leave_game.py

docker container stop postgres