#!/bin/bash

cd sprint2/problems/static_content/solution || exit 1
mkdir -p build
cd build
conan install ..
cmake ..
cmake --build . -j $(nproc)
