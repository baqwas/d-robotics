#!/usr/bin/env python3
# ============================================================================
# File:        file_media_pipeline.py
# Project:     d-robotics (ParkCircus Productions)
# License:     MIT
# Version:     0.2.0
# Description: Phase 2 camera-free image and video file inspection and media
#              artifact pipeline for RDK X3 with structured JSON output.
# ============================================================================

"""Inspect local image or video files on RDK X3 without requiring a camera."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import socket
import sys
from typing import Any

try:
    import cv2  # type: ignore[import-not-found]

    _HAS_CV2 = True
except ImportError:
    cv2 = None
    _HAS_CV2 = False


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mkv", ".mov", ".h264", ".h265", ".264", ".265"}


def utc_waqt() -> str:
    """Return current UTC timestamp in ISO-8601 format without offset suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def default_device_id() -> str:
    """Return short hostname as default DeviceId."""
    host = socket.gethostname().strip()
    if not host:
        return "rdkx3-node"
    return host.split(".")[0]


def emit_json(payload: dict[str, Any]) -> None:
    """Emit a single JSON status record."""
    print(json.dumps(payload, indent=2), flush=True)


def probe_media_metadata(input_path: Path) -> dict[str, Any]:
    """Extract basic file and optional OpenCV frame/dimension details."""
    stat = input_path.stat()
    ext = input_path.suffix.lower()

    if ext in IMAGE_EXTENSIONS:
        media_kind = "image"
    elif ext in VIDEO_EXTENSIONS:
        media_kind = "video"
    else:
        media_kind = "unknown"

    meta: dict[str, Any] = {
        "input_path": str(input_path.resolve()),
        "extension": ext,
        "media_kind": media_kind,
        "size_bytes": stat.st_size,
        "opencv_available": _HAS_CV2,
        "width": None,
        "height": None,
        "frame_count": None,
        "fps": None,
    }

    if not _HAS_CV2 or cv2 is None:
        return meta

    if media_kind == "image":
        img = cv2.imread(str(input_path))
        if img is not None:
            height, width = img.shape[:2]
            meta["width"] = int(width)
            meta["height"] = int(height)
            meta["frame_count"] = 1
    else:
        cap = cv2.VideoCapture(str(input_path))
        try:
            if cap.isOpened():
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
                frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
                fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
                meta["width"] = width if width > 0 else None
                meta["height"] = height if height > 0 else None
                meta["frame_count"] = frames if frames > 0 else None
                meta["fps"] = round(fps, 3) if fps > 0 else None
        finally:
            cap.release()

    return meta


def write_and_verify_artifact(output_path: Path, summary: dict[str, Any]) -> dict[str, Any]:
    """Write a pipeline manifest/artifact and verify it exists and is non-empty."""
    if output_path.parent:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
        fh.write("\n")

    if not output_path.exists() or not output_path.is_file():
        raise RuntimeError(f"Output artifact missing after write: {output_path}")

    out_size = output_path.stat().st_size
    if out_size <= 0:
        raise RuntimeError(f"Output artifact is empty (0 bytes): {output_path}")

    return {
        "output_path": str(output_path.resolve()),
        "output_size_bytes": out_size,
        "output_verified": True,
    }


def run_pipeline(input_path: Path, output_path: Path | None, device_id: str) -> int:
    """Validate and inspect input media file, optionally writing an output artifact."""
    if not input_path.exists() or not input_path.is_file():
        print(f"Error: input media file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        record: dict[str, Any] = {
            "DeviceId": device_id,
            "Waqt": utc_waqt(),
            "status": "ok",
        }
        record.update(probe_media_metadata(input_path))

        if output_path is not None:
            artifact_info = write_and_verify_artifact(output_path, record)
            record.update(artifact_info)

        emit_json(record)
        return 0

    except Exception as exc:
        emit_json(
            {
                "DeviceId": device_id,
                "Waqt": utc_waqt(),
                "status": "error",
                "input_path": str(input_path),
                "error": str(exc),
            }
        )
        return 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="RDK X3 Phase 2 camera-free image/video file inspection lab"
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to local image (.jpg/.png) or video (.mp4/.h264) file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output artifact path to write and verify",
    )
    parser.add_argument(
        "--device-id",
        type=str,
        default=default_device_id(),
        help="DeviceId tag in emitted JSON records (default: short hostname)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    return run_pipeline(
        input_path=args.input,
        output_path=args.output,
        device_id=args.device_id,
    )


if __name__ == "__main__":
    sys.exit(main())
