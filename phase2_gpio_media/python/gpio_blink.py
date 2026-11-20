#!/usr/bin/env python3
# ============================================================================
# File:        gpio_blink.py
# Project:     d-robotics (ParkCircus Productions)
# License:     MIT
# Version:     0.2.0
# Description: Phase 2 40-pin GPIO ribbon digital output lab for RDK X3 using
#              Hobot.GPIO with safe cleanup and optional dry-run simulation.
# ============================================================================

"""Blink a 3.3V GPIO pin on the D-Robotics RDK X3 40-pin ribbon header."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import signal
import socket
import sys
import time
from typing import Any

try:
    import Hobot.GPIO as GPIO  # type: ignore[import-not-found]

    _HAS_HOBOT_GPIO = True
except ImportError:
    GPIO = None
    _HAS_HOBOT_GPIO = False


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


def run_blink(pin: int, interval: float, cycles: int, device_id: str, dry_run: bool) -> int:
    """Run GPIO LED blink loop with guaranteed cleanup."""
    use_hardware = _HAS_HOBOT_GPIO and not dry_run
    mode_label = "hardware_hobot_gpio" if use_hardware else "simulated_dry_run"

    if not use_hardware and not dry_run and not _HAS_HOBOT_GPIO:
        print(
            "Note: Hobot.GPIO not found in current environment; running in simulated_dry_run mode.",
            file=sys.stderr,
        )

    gpio_initialized = False
    completed_cycles = 0

    try:
        if use_hardware:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
            gpio_initialized = True

        emit_event(
            {
                "DeviceId": device_id,
                "Waqt": utc_waqt(),
                "pin": pin,
                "mode": mode_label,
                "event": "started",
            }
        )

        while not _STOP_REQUESTED:
            if cycles > 0 and completed_cycles >= cycles:
                break

            if use_hardware:
                GPIO.output(pin, GPIO.HIGH)
            emit_event(
                {
                    "DeviceId": device_id,
                    "Waqt": utc_waqt(),
                    "pin": pin,
                    "mode": mode_label,
                    "state": "HIGH",
                    "cycle": completed_cycles + 1,
                }
            )
            time.sleep(interval)

            if _STOP_REQUESTED:
                break

            if use_hardware:
                GPIO.output(pin, GPIO.LOW)
            emit_event(
                {
                    "DeviceId": device_id,
                    "Waqt": utc_waqt(),
                    "pin": pin,
                    "mode": mode_label,
                    "state": "LOW",
                    "cycle": completed_cycles + 1,
                }
            )
            time.sleep(interval)

            completed_cycles += 1

        emit_event(
            {
                "DeviceId": device_id,
                "Waqt": utc_waqt(),
                "pin": pin,
                "mode": mode_label,
                "event": "completed",
                "cycles_completed": completed_cycles,
            }
        )
        return 0

    except Exception as exc:
        emit_event(
            {
                "DeviceId": device_id,
                "Waqt": utc_waqt(),
                "pin": pin,
                "mode": mode_label,
                "event": "error",
                "error": str(exc),
            }
        )
        return 1

    finally:
        if gpio_initialized and GPIO is not None:
            try:
                GPIO.output(pin, GPIO.LOW)
                GPIO.cleanup()
            except Exception as cleanup_exc:
                print(f"Warning: GPIO cleanup issue: {cleanup_exc}", file=sys.stderr)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="RDK X3 Phase 2 40-pin GPIO ribbon LED blink lab"
    )
    parser.add_argument(
        "--pin",
        type=int,
        default=7,
        help="40-pin header BOARD pin number (default: 7)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.5,
        help="Half-period delay in seconds between HIGH and LOW (default: 0.5)",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=6,
        help="Number of HIGH/LOW blink cycles; 0 runs until interrupted (default: 6)",
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
        help="Force simulated mode without touching GPIO hardware",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    if args.pin <= 0:
        print("Error: --pin must be a positive integer.", file=sys.stderr)
        return 2
    if args.interval <= 0:
        print("Error: --interval must be greater than 0.", file=sys.stderr)
        return 2
    if args.cycles < 0:
        print("Error: --cycles cannot be negative.", file=sys.stderr)
        return 2

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    return run_blink(
        pin=args.pin,
        interval=args.interval,
        cycles=args.cycles,
        device_id=args.device_id,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    sys.exit(main())
