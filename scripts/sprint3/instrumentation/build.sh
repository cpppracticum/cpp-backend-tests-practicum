#!/bin/bash

cd sprint3/problems/instrumentation/solution || exit 1
g++ -O3 *.cpp -o event2dot
