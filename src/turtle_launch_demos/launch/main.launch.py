"""
Actividad 2: Argumentos y Lanzamiento Jerarquico (archivo PRINCIPAL)
----------------------------------------------------------------------
Incluye subs_events.launch.py pasandole argumentos por medio de
sustituciones (namespace de destino y valores para el color de fondo).

Uso:
    ros2 launch turtle_launch_demos main.launch.py
"""

from launch_ros.substitutions import FindPackageShare
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, TextSubstitution


def generate_launch_description():
    colors = {
        "background_r": "200"
    }

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare("turtle_launch_demos"),
                    "launch",
                    "subs_events.launch.py"
                ])
            ]),
            launch_arguments={
                "turtlesim_ns": "turtlesim2",
                "use_provided_red": "True",
                "new_background_r": TextSubstitution(text=str(colors["background_r"]))
            }.items()
        ),
    ])
