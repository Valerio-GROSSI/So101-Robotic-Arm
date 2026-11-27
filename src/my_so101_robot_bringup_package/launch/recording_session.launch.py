from launch import LaunchDescription, LaunchService
from launch.actions import DeclareLaunchArgument, OpaqueFunction, IncludeLaunchDescription, ExecuteProcess
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration, PythonExpression, EnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

import os
import yaml

def launch_setup(context, *args, **kwargs):
    publisher_use_mock_hardware = LaunchConfiguration("publisher_use_mock_hardware")
    publisher_mock_sensor_commands = LaunchConfiguration("publisher_mock_sensor_commands")
    publisher_usb_port = LaunchConfiguration("publisher_usb_port")
    publisher_recalibrate = LaunchConfiguration("publisher_recalibrate")
    publisher_arm = LaunchConfiguration("publisher_arm")
    publisher_namespace = LaunchConfiguration("publisher_namespace")
    publisher_use_world_link = LaunchConfiguration("publisher_use_world_link")
    publisher_use_world_link_value = LaunchConfiguration("publisher_use_world_link").perform(context).lower()
    publisher_base_xyz = LaunchConfiguration("publisher_base_xyz")
    publisher_base_rpy = LaunchConfiguration("publisher_base_rpy")

    use_sim = LaunchConfiguration("use_sim")
    sim_gazebo = LaunchConfiguration("sim_gazebo")
    sim_gazebo_classic = LaunchConfiguration("sim_gazebo_classic")
    subscriber_use_mock_hardware = LaunchConfiguration("subscriber_use_mock_hardware")
    subscriber_mock_sensor_commands = LaunchConfiguration("subscriber_mock_sensor_commands")
    subscriber_usb_port = LaunchConfiguration("subscriber_usb_port")
    subscriber_recalibrate = LaunchConfiguration("subscriber_recalibrate")
    subscriber_arm = LaunchConfiguration("subscriber_arm")
    subscriber_namespace = LaunchConfiguration("subscriber_namespace")
    subscriber_use_world_link = LaunchConfiguration("subscriber_use_world_link")
    subscriber_base_xyz = LaunchConfiguration("subscriber_base_xyz")
    subscriber_base_rpy = LaunchConfiguration("subscriber_base_rpy")
    controller = LaunchConfiguration("controller")
    use_moveit = LaunchConfiguration("use_moveit")
    headless = LaunchConfiguration("headless")
    enable_static_cam = LaunchConfiguration("enable_static_cam")
    enable_wrist_cam = LaunchConfiguration("enable_wrist_cam")
    cam_static_xyz = LaunchConfiguration("cam_static_xyz")
    cam_static_rpy = LaunchConfiguration("cam_static_rpy")
    cam_wrist_xyz = LaunchConfiguration("cam_wrist_xyz")
    cam_wrist_rpy = LaunchConfiguration("cam_wrist_rpy")
    cameras_config = LaunchConfiguration("cameras_config")

    use_rviz = LaunchConfiguration("use_rviz")
    use_rviz_value = (LaunchConfiguration('use_rviz').perform(context).lower() == "true")
    use_unique_rviz = LaunchConfiguration("use_unique_rviz")
    use_unique_rviz_value = (LaunchConfiguration("use_unique_rviz").perform(context).lower() == "true")

    rviz_config= PathJoinSubstitution([FindPackageShare("so101_robot_description"), "rviz", "dual_arm.rviz"])

    pub_arm_joint_topic = PythonExpression(["'/' + '", 
                                            publisher_namespace, 
                                            "' + '/joint_states'"])
    sub_arm_jtc_topic = PythonExpression(["'/' + '",
                                         subscriber_namespace,
                                         "' + '/joint_trajectory_controller/joint_trajectory'"])
    sub_arm_fcc_topic = PythonExpression(["'/' + '",
                                         subscriber_namespace,
                                         "' + '/forward_position_controller/commands'"])

    use_rviz_split = "false"
    use_rviz_unique = "false"

    if use_rviz_value:
        if use_unique_rviz_value:
            use_rviz_unique = "true"
            publisher_use_world_link_value = "true"
        else:
            use_rviz_split = "true"

    publisher_launch_arguments = {
        "use_mock_hardware": publisher_use_mock_hardware,
        "mock_sensor_commands": publisher_mock_sensor_commands, 
        "usb_port": publisher_usb_port,
        "recalibrate": publisher_recalibrate,
        "arm": publisher_arm,
        "namespace": publisher_namespace,
        "use_world_link": publisher_use_world_link_value,
        "base_xyz": publisher_base_xyz,
        "base_rpy": publisher_base_rpy,
        "use_rviz": use_rviz_split,
    }

    subscriber_launch_arguments = {
        "use_sim": use_sim,
        "sim_gazebo": sim_gazebo,
        "sim_gazebo_classic": sim_gazebo_classic,
        "use_mock_hardware": subscriber_use_mock_hardware,
        "mock_sensor_commands": subscriber_mock_sensor_commands,
        "usb_port": subscriber_usb_port,
        "recalibrate": subscriber_recalibrate,
        "arm": subscriber_arm,
        "namespace": subscriber_namespace,
        "use_world_link": subscriber_use_world_link,
        "base_xyz": subscriber_base_xyz,
        "base_rpy": subscriber_base_rpy,
        "controller": controller,
        "use_moveit": use_moveit,
        "use_rviz": use_rviz_split,
        "headless": headless,
        "enable_static_cam": enable_static_cam,
        "enable_wrist_cam": enable_wrist_cam,
        "cam_static_xyz": cam_static_xyz,
        "cam_static_rpy": cam_static_rpy,
        "cam_wrist_xyz": cam_wrist_xyz,
        "cam_wrist_rpy": cam_wrist_rpy,
        "cameras_config": cameras_config,
    }

    recording_config_file = LaunchConfiguration("recording_config_file")
    root_dir = LaunchConfiguration("root_dir")
    experiment_name = LaunchConfiguration("experiment_name")
    task = LaunchConfiguration("task")

    rerun_env_dir = LaunchConfiguration("rerun_env_dir")
    use_rerun = LaunchConfiguration("use_rerun")
    
    publisher_arm_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('so101_robot_bringup'),
                'launch',
                'publisher_arm.launch.py',
            ])),
            launch_arguments=publisher_launch_arguments.items(),
        )

    subscriber_arm_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('so101_robot_bringup'),
                'launch',
                'subscriber_arm_vision.launch.py',
            ])),
            launch_arguments=subscriber_launch_arguments.items(),
        )

    teleop = Node(package="so101_robot_bringup",
                  executable="teleop",
                  name="publisher_subscriber_relay",
                  output="screen",
                  parameters=[
                      {
                        "controller": controller,
                        "pub_arm_joint_topic": pub_arm_joint_topic,
                        "sub_arm_jtc_topic": sub_arm_jtc_topic,
                        "sub_arm_fcc_topic": sub_arm_fcc_topic,
                      },
                  ],
            )

    rviz_node = Node(
                    package="rviz2",
                    executable="rviz2",
                    output="screen",
                    arguments=["-d", rviz_config],
                    condition=IfCondition(use_rviz_unique),
                )

    recorder_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('episode_recorder'),
                'launch',
                'recorder.launch.py'
            ])),
            launch_arguments={
                "params_file": recording_config_file,
                "root_dir": root_dir,
                "experiment_name": experiment_name,
                "task": task,
            }.items(),
        )

    # rerun_bridge_proc = ExecuteProcess(
    #     cmd=[
    #         "pixi",
    #         "run",
    #         "bridge",
    #         "--",
    #         # "--wrist", rerun_wrist,
    #         # "--overhead", rerun_overhead,
    #         # "--joint-states", rerun_joint_states,
    #         # "--forward-commands", rerun_forward_cmds,
    #         # "--joint-trajectory", rerun_joint_traj,
    #     ],
    #     cwd=rerun_env_dir,
    #     additional_env={"PYTHONUNBUFFERED": "1"},
    #     condition=IfCondition(use_rerun),
    #     output="screen",
    # )

    return [
        publisher_arm_launch,
        subscriber_arm_launch,
        teleop,
        rviz_node,
        recorder_launch,
        rerun_bridge_proc,
    ]

def generate_launch_description():
    publisher_use_mock_hardware_arg = DeclareLaunchArgument("publisher_use_mock_hardware", default_value="false", description="Start robot with mock hardware mirroring command to its states.")
    publisher_mock_sensor_commands_arg = DeclareLaunchArgument("publisher_mock_sensor_commands", default_value="true", description="Start robot with mock sensor commands.")
    publisher_usb_port_arg = DeclareLaunchArgument("publisher_usb_port", default_value="/dev/ttyACM0")
    publisher_recalibrate_arg = DeclareLaunchArgument("publisher_recalibrate", default_value="false")
    publisher_arm_arg = DeclareLaunchArgument("publisher_arm", default_value="leader", choices=["leader", "follower"], description="Modèle du bras")
    publisher_namespace_arg = DeclareLaunchArgument("publisher_namespace", default_value="leader")
    publisher_use_world_link_arg = DeclareLaunchArgument("publisher_use_world_link", default_value="false")
    publisher_base_xyz_arg = DeclareLaunchArgument("publisher_base_xyz", default_value="0.0 -2.0 0.0")
    publisher_base_rpy_arg = DeclareLaunchArgument("publisher_base_rpy", default_value="0.0 0.0 0.0")

    use_sim_arg = DeclareLaunchArgument("use_sim", default_value='false')
    sim_gazebo_arg = DeclareLaunchArgument("sim_gazebo", default_value='true')
    sim_gazebo_classic_arg = DeclareLaunchArgument("sim_gazebo_classic", default_value='false')
    subscriber_use_mock_hardware_arg = DeclareLaunchArgument("subscriber_use_mock_hardware", default_value="false", description="Start robot with mock hardware mirroring command to its states.")
    subscriber_mock_sensor_commands_arg = DeclareLaunchArgument("subscriber_mock_sensor_commands", default_value="true", description="Start robot with mock sensor commands.")
    subscriber_usb_port_arg = DeclareLaunchArgument("subscriber_usb_port", default_value="/dev/ttyACM1")
    subscriber_recalibrate_arg = DeclareLaunchArgument("subscriber_recalibrate", default_value="false")
    subscriber_arm_arg = DeclareLaunchArgument("subscriber_arm", default_value="follower", choices=["leader", "follower"], description="Modèle du bras")
    subscriber_namespace_arg = DeclareLaunchArgument("subscriber_namespace", default_value="follower")
    subscriber_use_world_link_arg = DeclareLaunchArgument("subscriber_use_world_link", default_value="true")
    subscriber_base_xyz_arg = DeclareLaunchArgument("subscriber_base_xyz", default_value="0.0 0.0 0.0")
    subscriber_base_rpy_arg = DeclareLaunchArgument("subscriber_base_rpy", default_value="0.0 0.0 0.0")
    controller_arg = DeclareLaunchArgument("controller", default_value="forward_position_controller", choices=["forward_position_controller", "joint_trajectory_controller"])
    use_moveit_arg = DeclareLaunchArgument("use_moveit", default_value="false")
    headless_arg = DeclareLaunchArgument("headless", default_value="false")
    enable_static_cam_arg = DeclareLaunchArgument("enable_static_cam", default_value="true")
    enable_wrist_cam_arg = DeclareLaunchArgument("enable_wrist_cam", default_value="true")
    cam_static_xyz_arg = DeclareLaunchArgument("cam_static_xyz", default_value="0.2 0.0 0.60")
    cam_static_rpy_arg = DeclareLaunchArgument("cam_static_rpy", default_value="0.0 1.5708 0.0")
    cam_wrist_xyz_arg = DeclareLaunchArgument("cam_wrist_xyz", default_value="0.0 0.0 -0.02")
    cam_wrist_rpy_arg = DeclareLaunchArgument("cam_wrist_rpy", default_value="-1.5708 0.0 -1.5708")

    cameras_config_arg = DeclareLaunchArgument("cameras_config", default_value=os.path.join(get_package_share_directory("so101_robot_bringup"), "config", "cameras", "so101_cameras.yaml"))

    use_rviz_arg = DeclareLaunchArgument("use_rviz", default_value="true")
    use_unique_rviz_arg = DeclareLaunchArgument("use_unique_rviz", default_value="false")

    recording_config_file_arg = DeclareLaunchArgument("recording_config_file", default_value=os.path.join(get_package_share_directory("so101_robot_bringup"), "config", "recording", "episode_recorder_so101.yaml"))
    root_dir_arg = DeclareLaunchArgument("root_dir", default_value=PathJoinSubstitution([EnvironmentVariable("ROS_HOME", default_value=PathJoinSubstitution([EnvironmentVariable("HOME"), ".ros"]))]))
    experiment_name_arg = DeclareLaunchArgument("experiment_name", default_value="pick_and_place")
    task_arg = DeclareLaunchArgument("task", default_value="")

    # export SO101_RERUN_ENV_DIR=/abs/path/to/tools/rerun_env
    rerun_env_dir_arg = DeclareLaunchArgument("rerun_env_dir", default_value=EnvironmentVariable("SO101_RERUN_ENV_DIR", default_value=""))
    use_rerun_arg = DeclareLaunchArgument("use_rerun", default_value="false")

    return LaunchDescription([
        publisher_use_mock_hardware_arg,
        publisher_mock_sensor_commands_arg,
        publisher_usb_port_arg,
        publisher_recalibrate_arg,
        publisher_arm_arg,
        publisher_namespace_arg,
        publisher_use_world_link_arg,
        publisher_base_xyz_arg,
        publisher_base_rpy_arg,
        use_sim_arg,
        sim_gazebo_arg,
        sim_gazebo_classic_arg,
        subscriber_use_mock_hardware_arg,
        subscriber_mock_sensor_commands_arg,
        subscriber_usb_port_arg,
        subscriber_recalibrate_arg,
        subscriber_arm_arg,
        subscriber_namespace_arg,
        subscriber_use_world_link_arg,
        subscriber_base_xyz_arg,
        subscriber_base_rpy_arg,
        controller_arg,
        use_moveit_arg,
        headless_arg,
        enable_static_cam_arg,
        enable_wrist_cam_arg,
        cam_static_xyz_arg,
        cam_static_rpy_arg,
        cam_wrist_xyz_arg,
        cam_wrist_rpy_arg,
        cameras_config_arg,
        use_rviz_arg,
        use_unique_rviz_arg,
        recording_config_file_arg,
        root_dir_arg,
        experiment_name_arg,
        task_arg,
        rerun_env_dir_arg,
        use_rerun_arg,
        OpaqueFunction(function = launch_setup),
    ])

if __name__ =="__main__":
    ld = generate_launch_description()

    ls = LaunchService()
    ls.include_launch_description(ld)
    ls.run()