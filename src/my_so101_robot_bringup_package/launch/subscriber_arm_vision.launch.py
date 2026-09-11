import os
from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument, OpaqueFunction, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node, SetParameter
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition

def launch_setup(context):

    use_sim = LaunchConfiguration("use_sim")
    use_sim_value = (LaunchConfiguration("use_sim").perform(context) == "true")
    sim_gazebo = LaunchConfiguration("sim_gazebo")
    sim_gazebo_value = (LaunchConfiguration("sim_gazebo").perform(context) == "true")
    sim_gazebo_classic = LaunchConfiguration("sim_gazebo_classic")
    use_mock_hardware = LaunchConfiguration("use_mock_hardware")
    mock_sensor_commands = LaunchConfiguration("mock_sensor_commands")
    usb_port = LaunchConfiguration("usb_port")
    recalibrate = LaunchConfiguration("recalibrate")
    arm = LaunchConfiguration("arm")
    arm_value = LaunchConfiguration("arm").perform(context)
    namespace = LaunchConfiguration("namespace")
    namespace_value = LaunchConfiguration("namespace").perform(context)
    use_world_link = LaunchConfiguration("use_world_link")
    base_xyz = LaunchConfiguration("base_xyz")
    base_rpy = LaunchConfiguration("base_rpy")
    controller = LaunchConfiguration("controller")
    use_moveit = LaunchConfiguration("use_moveit")
    use_rviz_value = (LaunchConfiguration("use_rviz").perform(context) == "true")   
    headless = LaunchConfiguration('headless')
    enable_static_cam = LaunchConfiguration("enable_static_cam")
    enable_wrist_cam = LaunchConfiguration("enable_wrist_cam")
    cam_static_xyz = LaunchConfiguration("cam_static_xyz")
    cam_static_rpy = LaunchConfiguration("cam_static_rpy")
    cam_wrist_xyz = LaunchConfiguration("cam_wrist_xyz")
    cam_wrist_rpy = LaunchConfiguration("cam_wrist_rpy")

    cameras_config = LaunchConfiguration("cameras_config")

    if use_sim_value:
        if sim_gazebo_value:
            rviz_config_file = f"{arm_value}_sim_gazebo.rviz"
        else:
            rviz_config_file = f"{arm_value}_sim_gazebo_classic.rviz"
    else:
        rviz_config_file = f"{arm_value}.rviz"

    if namespace_value:
            rviz_config_file = f"ns_{rviz_config_file}"
            
    rviz_config = PathJoinSubstitution([FindPackageShare("so101_robot_description"), "rviz", "vision", rviz_config_file])

    subscriber_arm_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("so101_robot_bringup"),
                "launch",
                "subscriber_arm.launch.py"
            ])
        ),
        launch_arguments={
            "use_sim": use_sim,
            "sim_gazebo": sim_gazebo,
            "sim_gazebo_classic": sim_gazebo_classic, 
            "use_mock_hardware": use_mock_hardware,
            "mock_sensor_commands": mock_sensor_commands,
            "usb_port": usb_port,
            "recalibrate": recalibrate,
            "arm": arm,
            "namespace": namespace,
            "use_world_link": use_world_link,
            "base_xyz": base_xyz,
            "base_rpy": base_rpy,
            "controller": controller,
            "use_moveit": use_moveit,
            "use_rviz": "false",
            "headless": headless,
            "enable_static_cam": enable_static_cam,
            "enable_wrist_cam": enable_wrist_cam,
            "cam_static_xyz": cam_static_xyz,
            "cam_static_rpy": cam_static_rpy,
            "cam_wrist_xyz": cam_wrist_xyz,
            "cam_wrist_rpy": cam_wrist_rpy,
        }.items()
    )

    cameras_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("so101_robot_bringup"),
                "launch",
                "cameras.launch.py"
            ])
        ),
        launch_arguments={
            "cameras_config": cameras_config,
            "namespace": namespace,
            "use_sim": use_sim,
            "sim_gazebo": sim_gazebo,
            "enable_static_cam": enable_static_cam,
            "enable_wrist_cam": enable_wrist_cam
        }.items()
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        output="screen",
        namespace=namespace,
        arguments=["-d", rviz_config],
    )

    actions = [
        subscriber_arm_launch,
        cameras_launch,
    ]

    if use_rviz_value:
        actions.append(rviz_node)
    
    return actions

def generate_launch_description():
    # use_sim = LaunchConfiguration('use_sim')

    use_sim_arg = DeclareLaunchArgument('use_sim', default_value='false')
    sim_gazebo_arg = DeclareLaunchArgument('sim_gazebo', default_value='true')
    sim_gazebo_classic_arg = DeclareLaunchArgument('sim_gazebo_classic', default_value='false')
    use_mock_hardware_arg = DeclareLaunchArgument("use_mock_hardware", default_value="false", description="Start robot with mock hardware mirroring command to its states.")
    mock_sensor_commands_arg = DeclareLaunchArgument("mock_sensor_commands", default_value="true", description="Start robot with mock sensor commands.")
    usb_port_arg = DeclareLaunchArgument("usb_port", default_value="/dev/ttyACM1")
    recalibrate_arg = DeclareLaunchArgument("recalibrate", default_value="false")
    arm_arg = DeclareLaunchArgument("arm", default_value="follower", choices=["leader", "follower"], description="Modèle du bras")
    namespace_arg = DeclareLaunchArgument("namespace", default_value="",)
    use_world_link_arg = DeclareLaunchArgument("use_world_link", default_value="false")
    base_xyz_arg = DeclareLaunchArgument("base_xyz", default_value="0.0 0.0 0.0")
    base_rpy_arg = DeclareLaunchArgument("base_rpy", default_value="0.0 0.0 0.0")
    controller_arg = DeclareLaunchArgument("controller", default_value="forward_position_controller", choices=["forward_position_controller", "joint_trajectory_controller"])
    use_moveit_arg = DeclareLaunchArgument("use_moveit", default_value="false")
    use_rviz_arg = DeclareLaunchArgument("use_rviz", default_value="false")
    headless_arg = DeclareLaunchArgument("headless", default_value="false")
    enable_static_cam_arg = DeclareLaunchArgument("enable_static_cam", default_value="false")
    enable_wrist_cam_arg = DeclareLaunchArgument("enable_wrist_cam", default_value="false")
    cam_static_xyz_arg = DeclareLaunchArgument("cam_static_xyz", default_value="0.2 0.0 0.60")
    cam_static_rpy_arg = DeclareLaunchArgument("cam_static_rpy", default_value="0.0 1.5708 0.0")
    cam_wrist_xyz_arg = DeclareLaunchArgument("cam_wrist_xyz", default_value="0.0 0.0 -0.02")
    cam_wrist_rpy_arg = DeclareLaunchArgument("cam_wrist_rpy", default_value="-1.5708 0.0 -1.5708")

    cameras_config_arg = DeclareLaunchArgument("cameras_config", default_value=os.path.join(get_package_share_directory("so101_robot_bringup"), "config", "cameras", "so101_cameras.yaml"))

    return LaunchDescription([
        use_sim_arg,
        sim_gazebo_arg,
        sim_gazebo_classic_arg,
        use_mock_hardware_arg,
        mock_sensor_commands_arg,
        usb_port_arg,
        recalibrate_arg,
        arm_arg,
        namespace_arg,
        use_world_link_arg,
        base_xyz_arg,
        base_rpy_arg,
        controller_arg,
        use_moveit_arg,
        use_rviz_arg,
        headless_arg,
        enable_static_cam_arg,
        enable_wrist_cam_arg,
        cam_static_xyz_arg,
        cam_static_rpy_arg,
        cam_wrist_xyz_arg,
        cam_wrist_rpy_arg,
        cameras_config_arg,
        # SetParameter(name="use_sim_time", value=use_sim),
        OpaqueFunction(function = launch_setup),
    ])