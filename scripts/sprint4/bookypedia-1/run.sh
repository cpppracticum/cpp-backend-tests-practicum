#!/bin/bash

REPO=${PWD}
SCRIPT_FOLDER=${REPO}/cpp-backend-tests-practicum/scripts/sprint4/bookypedia-1
NETWORK_NAME=docker_network

bash ${SCRIPT_FOLDER}/build.sh

docker network rm $NETWORK_NAME

DOCKER_NETWORK=$(docker network create $NETWORK_NAME)

docker container stop postgres
docker container rm postgres
docker run --rm --name postgres --network $NETWORK_NAME -e POSTGRES_HOST_AUTH_METHOD=trust -d postgres

sleep 5s # wait while postgres is setting up

docker run --rm --name bookypedia-1 -v /results:${SCRIPT_FOLDER}/results --network $NETWORK_NAME --env-file ${SCRIPT_FOLDER}/.env bookypedia-1

docker container stop postgres
docker network rm $NETWORK_NAME

rm ${SCRIPT_FOLDER}/test_s04_bookypedia-1.py
rm ${SCRIPT_FOLDER}/bookypedia