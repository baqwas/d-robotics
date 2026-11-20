#!/usr/bin/env python3
"""File-based BPU YOLO inference starter for D-Robotics RDK X3."""

from __future__ import annotations

import argparse
import datetime
import json
import os
import socket
import sys
from pathlib import Path
from typing import Any


def resolve_device_id(explicit_id: str | None) -> str:
    if explicit_id:
        return explicit_id.strip()
    env_host = os.environ.get("WIFI_HOSTNAME_DEFAULT", "").strip()
    if env_host:
        return env_host
    return socket.gethostname().strip() or "unknown-device"


def current_waqt() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run file-based YOLO inference (or dry-run/stub) on RDK X3."
    )
    parser.add_argument("--input", required=True, help="Path to input image, video, or sample file")
    parser.add_argument("--model", default="", help="Path to compiled BPU .bin model file")
    parser.add_argument("--output", default="", help="Optional path to write JSON summary")
    parser.add_argument("--device-id", default="", help="Override DeviceId")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in deterministic simulated stub mode without live BPU execution",
    )
    return parser


def run_inference(args: argparse.Namespace) -> dict[str, Any]:
    input_path = Path(args.input)
    model_path = Path(args.model) if args.model else None

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    stat = input_path.stat()
    ext = input_path.suffix.lower()
    if ext in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
        media_kind = "image"
    elif ext in {".mp4", ".avi", ".mkv", ".mov", ".h264", ".h265"}:
        media_kind = "video"
    else:
        media_kind = "file_fixture"

    model_present = bool(model_path and model_path.exists())
    stub_mode = bool(args.dry_run or not model_present)

    detections: list[dict[str, Any]] = []
    if stub_mode:
        detections.append(
            {
                "label": "stub_person",
                "score": 0.87,
                "bbox": [64, 48, 220, 340],
            }
        )

    payload: dict[str, Any] = {
        "DeviceId": resolve_device_id(args.device_id),
        "Waqt": current_waqt(),
        "status": "ok",
        "mode": "simulated_stub" if stub_mode else "bpu_ready",
        "input_path": str(input_path),
        "size_bytes": stat.st_size,
        "media_kind": media_kind,
        "model_path": str(model_path) if model_path else "",
        "model_present": model_present,
        "detections": detections,
    }

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        payload["output_path"] = str(out_path)
        payload["output_verified"] = out_path.exists() and out_path.stat().st_size > 0

    return payload


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = run_inference(args)
    except Exception as exc:
        err_payload = {
            "DeviceId": resolve_device_id(args.device_id),
            "Waqt": current_waqt(),
            "status": "error",
            "error": str(exc),
        }
        print(json.dumps(err_payload, indent=2))
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
