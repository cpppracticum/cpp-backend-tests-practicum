cmake_minimum_required(VERSION 3.15)
project(game_server CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Boost REQUIRED)
find_package(Threads REQUIRED)

file(GLOB_RECURSE SOURCES "src/*.cpp" "src/*.h")

add_executable(game_server ${SOURCES})

target_compile_definitions(game_server PRIVATE BOOST_BEAST_USE_STD_STRING_VIEW)

target_link_libraries(game_server PRIVATE 
    CONAN_PKG::boost 
    Threads::Threads
)

if(WIN32)
    target_compile_definitions(game_server PRIVATE _WIN32_WINNT=0x0A00)
    target_link_libraries(game_server PRIVATE ws2_32 mswsock)
endif()
