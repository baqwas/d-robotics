from glob import glob
from setuptools import setup

package_name = 'rdk_yolo_file_pkg'

setup(
    name=package_name,
    version='0.3.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Reza Wajih',
    maintainer_email='dev@parkcircus.org',
    description='Phase 3 file-based publisher and BPU YOLO stub detector nodes for RDK X3.',
    license='MIT',
    entry_points={
        'console_scripts': [
            'file_feeder_node = rdk_yolo_file_pkg.file_feeder_node:main',
            'yolo_file_detector_node = rdk_yolo_file_pkg.yolo_file_detector_node:main',
        ],
    },
)
