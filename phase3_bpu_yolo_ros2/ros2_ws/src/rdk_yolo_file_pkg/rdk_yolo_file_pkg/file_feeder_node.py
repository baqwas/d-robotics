#!/usr/bin/env python3
"""Publish file bytes as a sensor_msgs/Image frame for camera-free ROS 2 testing."""

from pathlib import Path
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image


class FileFeederNode(Node):
    def __init__(self) -> None:
        super().__init__("file_feeder_node")
        self.declare_parameter("input_path", "/tmp/board_check.txt")
        self.declare_parameter("period_sec", 2.0)

        self.input_path = Path(self.get_parameter("input_path").value)
        period = float(self.get_parameter("period_sec").value)

        self.pub = self.create_publisher(Image, "/rdk/file_frame", 10)
        self.timer = self.create_timer(period, self.publish_frame)
        self.get_logger().info(f"Feeding frames from {self.input_path} every {period}s")

    def publish_frame(self) -> None:
        if not self.input_path.exists():
            self.get_logger().warn(f"Missing input file: {self.input_path}")
            return

        payload = self.input_path.read_bytes()
        msg = Image()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "file_input"
        msg.height = 1
        msg.width = len(payload)
        msg.encoding = "mono8"
        msg.is_bigendian = False
        msg.step = len(payload)
        msg.data = list(payload)
        self.pub.publish(msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = FileFeederNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
