#!/usr/bin/env python3
"""Consume /rdk/file_frame and publish stub YOLO detections with DeviceId & Waqt."""

import datetime
import json
import os
import socket
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String


def resolve_device_id() -> str:
    env_host = os.environ.get("WIFI_HOSTNAME_DEFAULT", "").strip()
    return env_host or socket.gethostname().strip() or "unknown-device"


def current_waqt() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


class YoloFileDetectorNode(Node):
    def __init__(self) -> None:
        super().__init__("yolo_file_detector_node")
        self.device_id = resolve_device_id()
        self.sub = self.create_subscription(Image, "/rdk/file_frame", self.on_frame, 10)
        self.pub = self.create_publisher(String, "/rdk/yolo_detections", 10)
        self.get_logger().info(f"YOLO stub detector ready on DeviceId={self.device_id}")

    def on_frame(self, msg: Image) -> None:
        result = {
            "DeviceId": self.device_id,
            "Waqt": current_waqt(),
            "status": "ok",
            "mode": "ros2_file_stub",
            "frame_bytes": len(msg.data),
            "detections": [
                {"label": "stub_person", "score": 0.85, "bbox": [40, 50, 200, 310]}
            ],
        }
        out_msg = String()
        out_msg.data = json.dumps(result)
        self.pub.publish(out_msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = YoloFileDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
