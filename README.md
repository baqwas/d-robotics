# 🤖 D-Robotics RDK X3 — Self-Paced Robotics, GPIO & Edge AI Curriculum

> 🧭 **Headless-First • Breadboard-Ready • Camera-Optional YOLO & ROS 2 Labs**

Welcome to **`baqwas/d-robotics`**, a structured, hands-on learning repository designed for students and embedded developers working with the **D-Robotics RDK X3** (Sunrise X3M SoC + 5 TOPS Dual-Core Bernoulli BPU).

All labs are designed to run **headlessly** over SSH using **JetBrains CLion** and **PyCharm Community Edition**, and support **image/video file inputs** so you can build and test full BPU YOLO inference and ROS 2 pipelines before attaching a live MIPI CSI camera.

[![Status](https://img.shields.io/badge/status-active%20curriculum-2ea44f?style=flat-square)](../../wiki)
[![Version](https://img.shields.io/badge/version-v0.1.0--draft-0969da?style=flat-square)](../../releases)
[![Release Date](https://img.shields.io/badge/updated-2026--11--18-1f6feb?style=flat-square)](../../commits)
[![License](https://img.shields.io/badge/license-MIT-informational?style=flat-square)](LICENSE)

[![C++](https://img.shields.io/badge/language-C++-00599C?style=flat-square&logo=cplusplus&logoColor=white)](phase2_gpio_media/cpp_cmake)
[![Python](https://img.shields.io/badge/language-Python-3776AB?style=flat-square&logo=python&logoColor=white)](phase2_gpio_media/python)
[![CMake](https://img.shields.io/badge/build-CMake-064F8C?style=flat-square&logo=cmake&logoColor=white)](phase2_gpio_media/cpp_cmake)
[![ROS 2](https://img.shields.io/badge/framework-ROS%202-22314E?style=flat-square&logo=ros&logoColor=white)](phase3_bpu_yolo_ros2/ros2_ws)
[![Target](https://img.shields.io/badge/hardware-RDK%20X3%20%7C%205%20TOPS%20BPU-6f42c1?style=flat-square)](../../wiki/Phase-1-Quick-Start-and-System-Setup)
[![Mode](https://img.shields.io/badge/workflow-Headless%20SSH%20%7C%20No--Camera%20Ready-0e8a16?style=flat-square)](../../wiki/Home)

[![Curriculum Status](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fbaqwas%2Fd-robotics%2Fmain%2Fstatus.json&style=flat-square)](../../wiki)
[![CI](https://github.com/baqwas/d-robotics/actions/workflows/ci.yml/badge.svg)](https://github.com/baqwas/d-robotics/actions/workflows/ci.yml)

---

## 🗺️ Curriculum Roadmap

| Phase | Module | Focus & Deliverables | Hardware / Input |
| :--- | :--- | :--- | :--- |
| 🟢 **Phase 1** | **Quick Start & System Setup** | Ubuntu 20.04/22.04 flashing, headless SSH/Wi-Fi, `srpi-config` bus enablement | RDK X3 + microSD + Serial/SSH |
| 🔵 **Phase 2** | **GPIO Ribbon & File-Based Media** | Python/C++ control via 40-pin ribbon breadboard (GPIO, PWM, I2C, SPI) & H.264/H.265 file pipelines | 40-pin Ribbon + Breadboard + Test Videos |
| 🟣 **Phase 3** | **BPU YOLO & ROS 2 Workflows** | Running pre-compiled YOLOv5/YOLOv8 `.bin` models on the 5 TOPS BPU & publishing ROS 2 topics from image/video feeds | Static Images & Video Clips (No Camera Required) |
| 🟠 **Phase 4** | **OpenExplorer Toolchain** | PyTorch/ONNX FP32 $\rightarrow$ INT8 quantization, calibration, and `.bin` compilation on x86_64 Docker | Linux Workstation + RDK X3 |

---

## 📖 Student Guides (GitHub Wiki)

All step-by-step instructions, wiring diagrams, and verification checkpoints live in the **[Project Wiki](../../wiki)**:

* 🧭 **[Wiki Home & Workstation Setup](../../wiki/Home)** — Color icon legend, headless IDE configuration (`CLion` / `PyCharm CE`), and lab rules
* 🟢 **[Phase 1: Quick Start & System Setup](../../wiki/Phase-1-Quick-Start-and-System-Setup)**
* 🔵 **[Phase 2: GPIO Ribbon & File Media Pipelines](../../wiki/Phase-2-GPIO-Ribbon-and-File-Media)**
* 🟣 **[Phase 3: BPU YOLO Inference & ROS 2 Nodes](../../wiki/Phase-3-BPU-YOLO-and-ROS2-Workflows)**
* 🟠 **[Phase 4: OpenExplorer Model Quantization](../../wiki/Phase-4-OpenExplorer-Model-Quantization)**
* 🛠️ **[Troubleshooting & Headless IDE Tips](../../wiki/Troubleshooting-and-Headless-IDE-Tips)**

---

## 📂 Repository Layout

```text
d-robotics/
├── README.md                    # 🧭 Overview & quick links
├── .gitignore                   # 🧹 Excludes build/, .idea/, *.bin, and heavy test media
├── scripts/
│   └── scaffold_phase.sh        # ⚙️ Workspace scaffolding & environment checks
├── phase1_setup/
│   └── verify_board.sh          # 🔍 CPU, BPU, and bus verification script
├── phase2_gpio_media/
│   ├── python/                  # 🐍 PyCharm CE GPIO & OpenCV/video CLI labs
│   └── cpp_cmake/               # ⚡ CLion CMake sysfs/libgpiod & media starters
├── phase3_bpu_yolo_ros2/
│   ├── yolo_file_infer/         # 🧠 Image/video BPU inference (Python & C++)
│   └── ros2_ws/                 # 🤖 ROS 2 image/video publisher & YOLO detector package
└── phase4_openexplorer/
    └── toolchain_templates/     # 🔧 Quantization YAML templates & ONNX checkers

## Platform  

* OS: Ubuntu 22.04.5 LTS aarch64  
* Host: hobot X3 PI V2.1  
* Kernel: 4.14.87  
* CPU: (4) @ 1.500 GHz  
* Memory: 814 MiB / 3930 MiB  
* Shell: bash 5.1.16  
* Resolution: 1920x1080  

# References
[D-Robotics RDK Suite](https://d-robotics.github.io/rdk_doc/en/RDK)
