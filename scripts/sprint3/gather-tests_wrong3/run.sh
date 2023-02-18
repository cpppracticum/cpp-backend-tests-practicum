#!/bin/bash

REPO=${PWD}

docker run --rm --entrypoint /app/build/collision_detection_tests gather-tests_wrong3  || [ $? -ne 0 ]