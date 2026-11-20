"""Launch file for rdk_yolo_file_pkg file feeder and YOLO stub detector."""

from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchContext, LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _build_nodes(context: LaunchContext):
    params_file = LaunchConfiguration("params_file").perform(context)
    input_path_override = LaunchConfiguration("input_path").perform(context).strip()
    period_sec_override = LaunchConfiguration("period_sec").perform(context).strip()

    feeder_overrides = {}
    if input_path_override:
        feeder_overrides["input_path"] = input_path_override
    if period_sec_override:
        feeder_overrides["period_sec"] = float(period_sec_override)

    feeder_params = [params_file]
    if feeder_overrides:
        feeder_params.append(feeder_overrides)

    return [
        Node(
            package="rdk_yolo_file_pkg",
            executable="file_feeder_node",
            name="file_feeder_node",
            output="screen",
            parameters=feeder_params,
        ),
        Node(
            package="rdk_yolo_file_pkg",
            executable="yolo_file_detector_node",
            name="yolo_file_detector_node",
            output="screen",
        ),
    ]


def generate_launch_description() -> LaunchDescription:
    pkg_share = Path(get_package_share_directory("rdk_yolo_file_pkg"))
    default_params = str(pkg_share / "config" / "file_feeder.yaml")

    return LaunchDescription([
        DeclareLaunchArgument(
            "params_file",
            default_value=default_params,
            description="Path to YAML parameter file for file_feeder_node.",
        ),
        DeclareLaunchArgument(
            "input_path",
            default_value="",
            description="Optional override for file_feeder_node input_path.",
        ),
        DeclareLaunchArgument(
            "period_sec",
            default_value="",
            description="Optional override for file_feeder_node period_sec.",
        ),
        OpaqueFunction(function=_build_nodes),
    ])
