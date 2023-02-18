#!/bin/bash

REPO=${PWD}

cd sprint4/problems/state_serialization/solution || exit 1
docker build -t state_serialization .
mkdir ${REPO}/sprint4/problems/state_serialization/volume
chmod 777 ${REPO}/sprint4/problems/state_serialization/volume
