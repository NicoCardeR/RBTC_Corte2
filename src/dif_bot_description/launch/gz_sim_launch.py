import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg = get_package_share_directory("dif_bot_description")
    gz_pkg = get_package_share_directory("ros_gz_sim")

    model = LaunchConfiguration("model")
    world = LaunchConfiguration("world")
    use_ros2_control = LaunchConfiguration("use_ros2_control")
    use_ekf = LaunchConfiguration("use_ekf")

    args = [
        DeclareLaunchArgument("model", default_value=os.path.join(
            pkg, "urdf", "dif_bot_description.urdf.xacro")),
        DeclareLaunchArgument("world", default_value=os.path.join(
            pkg, "worlds", "dif_bot_world.sdf")),
        DeclareLaunchArgument("rviz", default_value="false"),
        DeclareLaunchArgument("use_ros2_control", default_value="false"),
        DeclareLaunchArgument("use_ekf", default_value="false"),
    ]

    # ParameterValue evita que ROS intente leer el XML como YAML (error original)
    robot_description = ParameterValue(
        Command(["xacro ", model,
                 " use_ros2_control:=", use_ros2_control,
                 " use_ekf:=", use_ekf]),
        value_type=str)

    rsp = Node(
        package="robot_state_publisher", executable="robot_state_publisher",
        output="screen",
        parameters=[{"robot_description": robot_description, "use_sim_time": True}])

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gz_pkg, "launch", "gz_sim.launch.py")),
        launch_arguments={"gz_args": ["-r ", world]}.items())

    spawn = Node(
        package="ros_gz_sim", executable="create", output="screen",
        arguments=["-name", "dif_bot", "-topic", "robot_description", "-z", "0.2"])

    bridge = Node(
        package="ros_gz_bridge", executable="parameter_bridge", output="screen",
        parameters=[{"config_file": os.path.join(pkg, "config", "gz_bridge.yaml"),
                     "use_sim_time": True}])

    rviz = Node(
        package="rviz2", executable="rviz2", output="screen",
        arguments=["-d", os.path.join(pkg, "rviz", "urdf_config.rviz")],
        parameters=[{"use_sim_time": True}],
        condition=IfCondition(LaunchConfiguration("rviz")))

    # Modo ros2_control (Practica 1)
    spawner_jsb = Node(
        package="controller_manager", executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager-timeout", "60"],
        condition=IfCondition(use_ros2_control))
    spawner_dd = Node(
        package="controller_manager", executable="spawner",
        arguments=["diff_drive_controller", "--controller-manager-timeout", "60",
                   "--controller-ros-args",
                   "-r /diff_drive_controller/cmd_vel:=/cmd_vel_stamped "
                   "-r /diff_drive_controller/odom:=/odom"],
        condition=IfCondition(use_ros2_control))

    stamper = ExecuteProcess(
        cmd=["python3", os.path.join(pkg, "scripts", "twist_stamper.py"),
             "--ros-args", "-p", "use_sim_time:=true"],
        output="screen", condition=IfCondition(use_ros2_control))

    # EKF opcional (Practica 2)
    ekf = Node(
        package="robot_localization", executable="ekf_node", name="ekf_filter_node",
        output="screen",
        parameters=[os.path.join(pkg, "config", "ekf.yaml"), {"use_sim_time": True}],
        remappings=[("odometry/filtered", "/odom_filtered")],
        condition=IfCondition(use_ekf))

    return LaunchDescription(args + [gz_sim, rsp, spawn, bridge, rviz,
                                     spawner_jsb, spawner_dd, stamper, ekf])
