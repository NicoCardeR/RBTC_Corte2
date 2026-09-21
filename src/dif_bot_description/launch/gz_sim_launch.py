"""
Actividad 8: Integracion con Gazebo Ignition (GZ Sim, Harmonic)
-------------------------------------------------------------------
1. Genera el URDF final a partir del xacro (robot_state_publisher).
2. Lanza GZ Sim con el mundo dif_bot_world.sdf.
3. Crea la entidad del robot en GZ Sim usando el nodo "create" de
   ros_gz_sim (equivalente ROS 2 / GZ Harmonic al antiguo
   "ros2 run gazebo_ros spawn_entity.py" de Gazebo clasico), leyendo
   la descripcion desde el topico /robot_description.
4. Activa ros_gz_bridge con la configuracion de config/gz_bridge.yaml
   para exponer cmd_vel, odom, tf, imu, scan y camera/image_raw en ROS 2.
5. (Opcional) Abre RViz para visualizar el robot simulado.

Uso:
    ros2 launch dif_bot_description gz_sim_launch.py
    ros2 launch dif_bot_description gz_sim_launch.py rviz:=false

Comando equivalente manual para crear la entidad (Entregable Actividad 8):
    ros2 run ros_gz_sim create -name dif_bot -topic robot_description -z 0.2
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_dif_bot = get_package_share_directory("dif_bot_description")
    pkg_ros_gz_sim = get_package_share_directory("ros_gz_sim")

    default_model_path = os.path.join(
        pkg_dif_bot, "urdf", "dif_bot_description.urdf.xacro")
    default_world_path = os.path.join(
        pkg_dif_bot, "worlds", "dif_bot_world.sdf")
    default_bridge_config = os.path.join(
        pkg_dif_bot, "config", "gz_bridge.yaml")
    default_rviz_config_path = os.path.join(
        pkg_dif_bot, "rviz", "urdf_config.rviz")

    model_arg = DeclareLaunchArgument(
        name="model", default_value=default_model_path,
        description="Ruta absoluta al archivo xacro/urdf del robot")
    world_arg = DeclareLaunchArgument(
        name="world", default_value=default_world_path,
        description="Ruta absoluta al mundo SDF de GZ Sim")
    rviz_arg = DeclareLaunchArgument(
        name="rviz", default_value="true",
        description="Lanzar o no RViz junto con la simulacion")

    robot_description = Command(["xacro ", LaunchConfiguration("model")])

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{
            "robot_description": robot_description,
            "use_sim_time": True,
        }]
    )

    # 1. Lanza GZ Sim (Harmonic) con el mundo indicado.
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={"gz_args": LaunchConfiguration("world")}.items()
    )

    # 2. Crea la entidad del robot en GZ Sim a partir de /robot_description.
    #    Equivale a "ros2 run ros_gz_sim create -name dif_bot -topic robot_description"
    spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name", "dif_bot",
            "-topic", "robot_description",
            "-z", "0.2",
        ],
        output="screen"
    )

    # 3. Puente ROS 2 <-> GZ Transport (cmd_vel, odom, tf, imu, scan, camara)
    bridge_node = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        parameters=[{
            "config_file": default_bridge_config,
            "use_sim_time": True,
        }],
        output="screen"
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", default_rviz_config_path],
        condition=IfCondition(LaunchConfiguration("rviz")),
        parameters=[{"use_sim_time": True}],
    )

    return LaunchDescription([
        model_arg,
        world_arg,
        rviz_arg,
        gz_sim,
        robot_state_publisher_node,
        spawn_entity,
        bridge_node,
        rviz_node,
    ])
