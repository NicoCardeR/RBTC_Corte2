"""
Actividad 1: Archivos Launch en ROS 2
--------------------------------------
Lanza dos nodos turtlesim_node en namespaces distintos (turtlesim1 y
turtlesim2) y un nodo mimic que hace que la tortuga 2 replique el
movimiento de la tortuga 1, usando remapeos de topicos.

Uso:
    ros2 launch turtle_launch_demos turtle_mimic.launch.py
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        # Tortuga 1: se ubica en el namespace "turtlesim1"
        Node(
            package="turtlesim",
            namespace="turtlesim1",
            executable="turtlesim_node",
            name="sim"
        ),
        # Tortuga 2: se ubica en el namespace "turtlesim2"
        Node(
            package="turtlesim",
            namespace="turtlesim2",
            executable="turtlesim_node",
            name="sim"
        ),
        # Nodo mimic: escucha la pose de turtlesim1 y publica velocidad
        # hacia turtlesim2 para que la imite.
        Node(
            package="turtlesim",
            executable="mimic",
            name="mimic",
            remappings=[
                ("/input/pose", "/turtlesim1/turtle1/pose"),
                ("/output/cmd_vel", "/turtlesim2/turtle1/cmd_vel"),
            ]
        ),
    ])
