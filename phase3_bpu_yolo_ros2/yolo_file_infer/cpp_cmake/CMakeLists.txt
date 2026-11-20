cmake_minimum_required(VERSION 3.16)
project(rdk_phase3_bpu_yolo CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

option(BUILD_STUB_BPU "Build BPU YOLO pipeline in stub mode without hardware BPU SDK" ON)

add_executable(bpu_yolo_file_infer src/bpu_yolo_stub.cpp)
if(BUILD_STUB_BPU)
    target_compile_definitions(bpu_yolo_file_infer PRIVATE BPU_STUB_MODE=1)
endif()
