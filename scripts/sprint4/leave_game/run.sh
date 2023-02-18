#!/bin/bash

REPO=${PWD}
SCRIPT_FOLDER=${REPO}/cpp-backend-tests-practicum/scripts/sprint4/leave_game
SOLUTION_FOLDER=${REPO}/sprint4/problems/leave_game/solution
GET_IP=${SCRIPT_FOLDER}/get_ip.py


bash $SCRIPT_FOLDER/build.sh

docker container stop postgres
docker container rm postgres
POSTGRES_ID=$(docker run --name postgres -e POSTGRES_HOST_AUTH_METHOD=trust -d postgres)

sleep 5s # wait while postgres is setting up

export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=Mys3Cr3t
export POSTGRES_HOST=$(python3 ${GET_IP} $POSTGRES_ID)
export POSTGRES_PORT=5432

echo $POSTGRES_HOST

export IMAGE_NAME=leave_game
export CONFIG_PATH=$SOLUTION_FOLDER/data/config.json

pytest --workers 4 --junitxml=leave_game.xml cpp-backend-tests-practicum/tests/test_s04_leave_game.py

docker container stop postgres