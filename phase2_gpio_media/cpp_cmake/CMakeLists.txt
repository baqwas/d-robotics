# ============================================================================
# File:        CMakeLists.txt
# Project:     d-robotics (ParkCircus Productions)
# License:     MIT
# Version:     0.2.0
# Description: CMake build configuration for Phase 2 C++ media and hardware
#              pipelines on RDK X3, supporting BUILD_STUB_HARDWARE for host
#              and CI builds.
# ============================================================================

cmake_minimum_required(VERSION 3.16)
project(rdk_x3_phase2_media LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(BUILD_STUB_HARDWARE "Build with non-hardware host stubs for CI and desktop testing" OFF)

add_executable(file_media_pipeline
    src/file_media_stub.cpp
)

target_include_directories(file_media_pipeline
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

if(BUILD_STUB_HARDWARE)
    target_compile_definitions(file_media_pipeline PRIVATE RDKX3_STUB_HARDWARE=1)
    message(STATUS "Building Phase 2 C++ targets in STUB mode")
else()
    target_compile_definitions(file_media_pipeline PRIVATE RDKX3_STUB_HARDWARE=0)
    message(STATUS "Building Phase 2 C++ targets for RDK X3 hardware")
endif()

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(file_media_pipeline PRIVATE -Wall -Wextra -Wpedantic)
endif()
