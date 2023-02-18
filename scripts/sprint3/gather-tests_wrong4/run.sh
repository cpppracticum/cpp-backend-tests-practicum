#!/bin/bash

REPO=${PWD}

docker run --rm --entrypoint /app/build/collision_detection_tests gather-tests_wrong4  || [ $? -ne 0 ]