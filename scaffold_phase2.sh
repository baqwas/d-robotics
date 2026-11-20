#!/usr/bin/env bash
# ==============================================================================
# File:        scaffold_phase2.sh
# Project:     d-robotics (ParkCircus Productions)
# Description: Creates the Phase 2 directory hierarchy and touches starter
#              files under ~/projects/d-robotics/phase2_gpio_media/.
# ==============================================================================

set -euo pipefail

PROJECT_ROOT="${HOME}/projects/d-robotics"
PHASE2_ROOT="${PROJECT_ROOT}/phase2_gpio_media"

DIRS=(
    "${PHASE2_ROOT}/python"
    "${PHASE2_ROOT}/cpp_cmake/include"
    "${PHASE2_ROOT}/cpp_cmake/src"
)

FILES=(
    "${PHASE2_ROOT}/python/gpio_blink.py"
    "${PHASE2_ROOT}/python/i2c_telemetry.py"
    "${PHASE2_ROOT}/python/file_media_pipeline.py"
    "${PHASE2_ROOT}/cpp_cmake/CMakeLists.txt"
    "${PHASE2_ROOT}/cpp_cmake/include/stub_hal.hpp"
    "${PHASE2_ROOT}/cpp_cmake/src/file_media_stub.cpp"
)

echo "Scaffolding Phase 2 structure in: ${PHASE2_ROOT}"

for dir in "${DIRS[@]}"; do
    mkdir -p "$dir"
done

for file in "${FILES[@]}"; do
    touch "$file"
done

echo "Done. Created directories and touched files:"
find "${PHASE2_ROOT}" -maxdepth 4 -ls
