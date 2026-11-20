#!/usr/bin/env python3
# ============================================================================
# File:        i2c_telemetry.py
# Project:     d-robotics (ParkCircus Productions)
# License:     MIT
# Version:     0.2.0
# Description: Phase 2 I2C bus scanner and register telemetry reader for RDK X3
#              using Linux /dev/i2c-* ioctl with structured JSON output and
#              optional dry-run mode.
# ============================================================================

"""Probe an I2C bus or read raw register bytes on the D-Robotics RDK X3."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import signal
import socket
import sys
import time
from typing import Any

I2C_SLAVE = 0x0703

_STOP_REQUESTED = False


def _handle_signal(signum: int, _frame: Any) -> None:
    global _STOP_REQUESTED
    _STOP_REQUESTED = True
    print(f"\nReceived signal {signum}; stopping cleanly...", file=sys.stderr)


def utc_waqt() -> str:
    """Return current UTC timestamp in ISO-8601 format without offset suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def default_device_id() -> str:
    """Return short hostname as default DeviceId."""
    host = socket.gethostname().strip()
    if not host:
        return "rdkx3-node"
    return host.split(".")[0]


def emit_event(event: dict[str, Any]) -> None:
    """Emit a single JSON telemetry/status line."""
    print(json.dumps(event), flush=True)


def scan_bus_hardware(bus: int, start_addr: int, end_addr: int) -> list[str]:
    """Scan I2C addresses on /dev/i2c-<bus> and return hex address strings."""
    dev_path = Path(f"/dev/i2c-{bus}")
    if not dev_path.exists():
        raise FileNotFoundError(f"I2C device node does not exist: {dev_path}")

    found: list[str] = []
    fd = os.open(str(dev_path), os.O_RDWR)
    try:
        for addr in range(start_addr, end_addr + 1):
            try:
                fcntl.ioctl(fd, I2C_SLAVE, addr)
                os.read(fd, 1)
                found.append(f"0x{addr:02x}")
            except OSError:
                continue
    finally:
        os.close(fd)

    return found


def read_register_hardware(bus: int, addr: int, reg: int, length: int) -> list[int]:
    """Read `length` bytes starting at register `reg` from I2C address `addr`."""
    dev_path = Path(f"/dev/i2c-{bus}")
    if not dev_path.exists():
        raise FileNotFoundError(f"I2C device node does not exist: {dev_path}")

    fd = os.open(str(dev_path), os.O_RDWR)
    try:
        fcntl.ioctl(fd, I2C_SLAVE, addr)
        os.write(fd, bytes([reg & 0xFF]))
        data = os.read(fd, length)
        return list(data)
    finally:
        os.close(fd)


def run_telemetry(
    bus: int,
    addr: int | None,
    reg: int,
    length: int,
    samples: int,
    interval: float,
    device_id: str,
    dry_run: bool,
) -> int:
    """Execute I2C scan or register polling loop."""
    use_hardware = not dry_run and Path(f"/dev/i2c-{bus}").exists()
    mode_label = "hardware_i2c" if use_hardware else "simulated_dry_run"

    if not use_hardware and not dry_run:
        print(
            f"Note: /dev/i2c-{bus} not present; running in simulated_dry_run mode.",
            file=sys.stderr,
        )

    count = 0
    try:
        while not _STOP_REQUESTED:
            if samples > 0 and count >= samples:
                break

            if addr is None:
                if use_hardware:
                    devices = scan_bus_hardware(bus, 0x03, 0x77)
                else:
                    devices = ["0x40", "0x76"]

                emit_event(
                    {
                        "DeviceId": device_id,
                        "Waqt": utc_waqt(),
                        "bus": bus,
                        "mode": mode_label,
                        "sample": count + 1,
                        "detected_addresses": devices,
                    }
                )
            else:
                if use_hardware:
                    raw_bytes = read_register_hardware(bus, addr, reg, length)
                else:
                    raw_bytes = [(reg + i + count) & 0xFF for i in range(length)]

                emit_event(
                    {
                        "DeviceId": device_id,
                        "Waqt": utc_waqt(),
                        "bus": bus,
                        "mode": mode_label,
                        "address": f"0x{addr:02x}",
                        "register": f"0x{reg:02x}",
                        "raw_bytes": raw_bytes,
                        "hex_bytes": [f"0x{b:02x}" for b in raw_bytes],
                        "sample": count + 1,
                    }
                )

            count += 1
            if samples > 0 and count >= samples:
                break
            if not _STOP_REQUESTED:
                time.sleep(interval)

        return 0

    except Exception as exc:
        emit_event(
            {
                "DeviceId": device_id,
                "Waqt": utc_waqt(),
                "bus": bus,
                "mode": mode_label,
                "event": "error",
                "error": str(exc),
            }
        )
        return 1


def _parse_int_auto(value: str) -> int:
    return int(value, 0)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="RDK X3 Phase 2 I2C bus scan and register telemetry reader"
    )
    parser.add_argument(
        "--bus",
        type=int,
        default=1,
        help="I2C bus number corresponding to /dev/i2c-<bus> (default: 1)",
    )
    parser.add_argument(
        "--addr",
        type=_parse_int_auto,
        default=None,
        help="Target 7-bit I2C device address (e.g., 0x40); omit to scan bus",
    )
    parser.add_argument(
        "--reg",
        type=_parse_int_auto,
        default=0x00,
        help="Starting register address when --addr is specified (default: 0x00)",
    )
    parser.add_argument(
        "--length",
        type=int,
        default=2,
        help="Number of bytes to read from --reg (default: 2)",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=1,
        help="Number of samples to capture; 0 runs until interrupted (default: 1)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Delay in seconds between samples (default: 1.0)",
    )
    parser.add_argument(
        "--device-id",
        type=str,
        default=default_device_id(),
        help="DeviceId tag in emitted JSON records (default: short hostname)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Force simulated telemetry without opening /dev/i2c-*",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    if args.bus < 0:
        print("Error: --bus must be a non-negative integer.", file=sys.stderr)
        return 2
    if args.addr is not None and not (0x03 <= args.addr <= 0x77):
        print("Error: --addr must be between 0x03 and 0x77.", file=sys.stderr)
        return 2
    if args.length <= 0 or args.length > 64:
        print("Error: --length must be between 1 and 64.", file=sys.stderr)
        return 2
    if args.samples < 0:
        print("Error: --samples cannot be negative.", file=sys.stderr)
        return 2
    if args.interval <= 0:
        print("Error: --interval must be greater than 0.", file=sys.stderr)
        return 2

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    return run_telemetry(
        bus=args.bus,
        addr=args.addr,
        reg=args.reg,
        length=args.length,
        samples=args.samples,
        interval=args.interval,
        device_id=args.device_id,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    sys.exit(main())
