#!/bin/bash

REPO=${PWD}

docker network rm test_docker_network
export $DOCKER_NETWORK=$(docker network create -d bridge test-docker-network)

docker run --rm --name --network $DOCKER_NETWORK postgres -e POSTGRES_HOST_AUTH_METHOD=trust -d postgres

export DELIVERY_APP=${REPO}/sprint4/problems/db_of_books/solution/build/book_manager
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=Mys3Cr3t
export POSTGRES_HOST=postgres
export POSTGRES_PORT=5432

pytest --junitxml=${GITHUB_WORKSPACE}/db_of_books.xml ${GITHUB_WORKSPACE}/cpp-backend-tests-practicum/tests/test_s04_db_of_books.py

docker cotainer stop postgres
docker network rm test_docker_network
