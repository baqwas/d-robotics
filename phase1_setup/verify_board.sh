#!/usr/bin/env bash
# ==============================================================================
# Project: D-Robotics RDK X3 Curriculum (baqwas/d-robotics)
# File:    phase1_setup/verify_board.sh
# Purpose: Non-destructive verification of CPU, BPU, buses, and ROS 2 environment
# License: MIT License | Copyright (c) ParkCircus Productions
# ==============================================================================
set -u

if [[ -t 1 && -z "${NO_COLOR:-}" ]]; then
  C_RESET='\033[0m'
  C_BOLD='\033[1m'
  C_GREEN='\033[32m'
  C_YELLOW='\033[33m'
  C_RED='\033[31m'
  C_CYAN='\033[36m'
else
  C_RESET=''
  C_BOLD=''
  C_GREEN=''
  C_YELLOW=''
  C_RED=''
  C_CYAN=''
fi

ok()   { printf "  ${C_GREEN}✔${C_RESET} %s\n" "$1"; }
warn() { printf "  ${C_YELLOW}▲${C_RESET} %s\n" "$1"; }
err()  { printf "  ${C_RED}✖${C_RESET} %s\n" "$1"; }
sec()  { printf "\n${C_BOLD}${C_CYAN}==> %s${C_RESET}\n" "$1"; }

printf "${C_BOLD}=== RDK X3 Phase 1 Verification ===${C_RESET}\n"
echo "Hostname: $(hostname)"
echo "Kernel:   $(uname -r)"
echo "OS:       $(grep -E '^(PRETTY_NAME)=' /etc/os-release 2>/dev/null | cut -d= -f2- | tr -d '\"')"

sec "CPU & Memory"
core_count=$(nproc 2>/dev/null || echo "0")
ok "CPU cores available: ${core_count}"
if [[ -r /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq ]]; then
  freq_khz=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq)
  ok "CPU0 freq: $((freq_khz / 1000)) MHz"
else
  warn "CPU0 scaling_cur_freq not readable"
fi
free -h | awk 'NR==1 || /Mem:/'

sec "BPU & Hardware Tools"
if compgen -G "/dev/bpu*" >/dev/null 2>&1; then
  ok "BPU device nodes present: $(ls -m /dev/bpu* 2>/dev/null)"
else
  warn "No /dev/bpu* device nodes found"
fi

for cmd in srpi-config hrut_somstatus hrt_model_exec; do
  if command -v "$cmd" >/dev/null 2>&1; then
    ok "Found tool: $cmd"
  else
    warn "Missing tool: $cmd"
  fi
done

sec "Peripheral Bus Nodes (/dev)"
bus_nodes=$(ls -m /dev/i2c-* /dev/spidev* /dev/ttyS* /dev/gpiochip* 2>/dev/null || true)
if [[ -n "$bus_nodes" ]]; then
  ok "Bus nodes: $bus_nodes"
else
  warn "No matching bus nodes yet (check srpi-config)"
fi

sec "ROS 2 Environment"
if [[ -n "${ROS_DISTRO:-}" ]]; then
  ok "ROS_DISTRO: $ROS_DISTRO"
else
  warn "ROS_DISTRO not currently exported in shell"
fi

found_ros=0
for setup_file in /opt/tros/*/setup.bash /opt/ros/*/setup.bash; do
  if [[ -r "$setup_file" ]]; then
    ok "Found ROS setup: $setup_file"
    found_ros=1
  fi
done
if [[ "$found_ros" -eq 0 ]]; then
  err "No ROS 2 setup.bash found under /opt/tros or /opt/ros"
fi
