#!/bin/bash

cd sprint4/problems/db_of_books/solution
mkdir build
cd build
conan install ..
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build .
