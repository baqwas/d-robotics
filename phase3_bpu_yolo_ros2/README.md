# Phase 3: BPU YOLO Inference & ROS 2 File-Based Nodes

Headless, camera-optional workflows for the D-Robotics RDK X3 (`raspbari55`):

- `yolo_file_infer/python/`: File-based YOLO inference & stub/dry-run runner
- `yolo_file_infer/cpp_cmake/`: CMake C++ starter/stub target for CLion
- `yolo_file_infer/models/`: Compiled BPU `.bin` models
- `yolo_file_infer/samples/`: Sample image/video test inputs
- `ros2_ws/src/rdk_yolo_file_pkg/`: ROS 2 file publisher and detection nodes
