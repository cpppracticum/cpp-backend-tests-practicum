#!/bin/bash

REPO=${PWD}

docker run --rm --entrypoint /app/build/collision_detection_tests gather-tests_wrong1  || [ $? -ne 0 ]