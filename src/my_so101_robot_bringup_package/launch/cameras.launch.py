import os
import yaml

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, IncludeLaunchDescription, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node, SetRemap, SetParameter
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition

def spawn_cameras(context):
    use_sim_value = (LaunchConfiguration("use_sim").perform(context).lower() == "true")
    sim_gazebo_value = (LaunchConfiguration('sim_gazebo').perform(context).lower() == "true")

    cameras_cfg = LaunchConfiguration("cameras_config").perform(context)
    namespace = LaunchConfiguration("namespace").perform(context)

    namespace_value = LaunchConfiguration("namespace").perform(context)
    prefix_value = f"{namespace_value}_" if namespace_value else ""

    enable_static_cam_value = (LaunchConfiguration("enable_static_cam").perform(context).lower() == "true")
    enable_wrist_cam_value = (LaunchConfiguration("enable_wrist_cam").perform(context).lower() == "true")

    with open(cameras_cfg, "r") as f:
        cfg = yaml.safe_load(f) or {}

    camera_nodes = []
    if not use_sim_value:
        for cam in cfg.get("cameras", []):
            name = cam["name"]
            ns = cam.get("namespace", "")
            ns = namespace
            cam_type = cam["camera_type"]
            param_path = cam["param_path"]

            if (
                cam_type == "v4l2_camera"
                and not enable_wrist_cam_value
            ):
                continue

            if (
                cam_type == "depthai_camera"
                and not enable_static_cam_value
            ):
                continue

            param_file = (
                param_path 
                if os.path.isabs(param_path)
                else os.path.join(get_package_share_directory("so101_robot_bringup"), "config", "cameras", param_path)
            )

            if cam_type  == "v4l2_camera":
                camera_nodes.append(
                    Node(
                        package="v4l2_camera",
                        executable="v4l2_camera_node",
                        name=name,
                        namespace=ns,
                        parameters=[param_file,
                                    {"frame_id": f"{prefix_value}wrist_camera_optical_frame"}
                                    ],
                        output="screen",
                        remappings=[
                            (
                                "image_raw",
                                f"/{prefix_value}{name}/image_raw",
                            ),
                            (
                                "image_raw/compressed",
                                f"/{prefix_value}{name}/image_raw/compressed",
                            ),
                            (
                                "image_raw/compressedDepth",
                                f"/{prefix_value}{name}/image_raw/compressedDepth",
                            ),
                            (
                                "image_raw/theora",
                                f"/{prefix_value}{name}/image_raw/theora",
                            ),
                            (
                                "camera_info",
                                f"/{prefix_value}{name}/camera_info",
                            ),
                        ],
                    )
                )
            elif cam_type == "depthai_camera":
                with open(param_file, "r") as f:
                    param_dico = yaml.safe_load(f) or {}
                    param_dico["name"] = name
                    param_dico["namespace"] = ""
                    param_dico["parent_frame"] = "static_camera_optical_frame"
                    # param_dico["parent_frame"] = f"{prefix_value}static_camera_optical_frame"
                    # camera_robot_description_topic = (f"/{namespace_value}/{name}/robot_description" if namespace_value else f"/{name}/robot_description")
                camera_nodes.append(
                    GroupAction([
                        SetRemap(
                            src="robot_description",
                            dst=f"/{name}/robot_description",
                        ),
                        SetRemap(
                            src="joint_states",
                            dst=f"/{name}/joint_states",
                        ),
                        IncludeLaunchDescription(
                            PythonLaunchDescriptionSource(
                                PathJoinSubstitution([
                                    FindPackageShare('depthai_ros_driver_v3'),
                                    'launch',
                                    'driver.launch.py',
                                ])),
                                launch_arguments=param_dico.items(),
                        ),
                    ])
                )
            else:
                raise RuntimeError(f"Unsupported camera_type: {cam_type}")

    gz_sim_camera_bridge_cam_wrist = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="gz_sim_camera_bridge_cam_wrist",
        namespace=namespace,
        arguments=[
            f"/{prefix_value}cam_wrist/image_raw"
            "@sensor_msgs/msg/Image"
            "[gz.msgs.Image",

            f"/{prefix_value}cam_wrist/camera_info"
            "@sensor_msgs/msg/CameraInfo"
            "[gz.msgs.CameraInfo",
        ],
        output="screen",
        condition=IfCondition(str(use_sim_value and sim_gazebo_value and enable_wrist_cam_value).lower()),
    )

    gz_sim_camera_bridge_cam_overhead = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="gz_sim_camera_bridge_cam_overhead",
        arguments=[
            "/cam_overhead/image_raw"
            "@sensor_msgs/msg/Image"
            "[gz.msgs.Image",

            "/cam_overhead/camera_info"
            "@sensor_msgs/msg/CameraInfo"
            "[gz.msgs.CameraInfo",
        ],
        output="screen",
        condition=IfCondition(str(use_sim_value and sim_gazebo_value and enable_static_cam_value).lower()),
    )

    return [
        *camera_nodes,
        gz_sim_camera_bridge_cam_wrist,
        gz_sim_camera_bridge_cam_overhead,
    ]

def generate_launch_description():
    # use_sim = LaunchConfiguration('use_sim')

    use_sim_arg = DeclareLaunchArgument('use_sim', default_value='false')
    sim_gazebo_arg = DeclareLaunchArgument('sim_gazebo', default_value='true')
    cameras_config_arg = DeclareLaunchArgument("cameras_config", default_value=os.path.join(get_package_share_directory("so101_robot_bringup"), "config", "cameras", "so101_cameras.yaml"))
    namespace_arg = DeclareLaunchArgument("namespace", default_value="follower")
    enable_static_cam_arg = DeclareLaunchArgument("enable_static_cam", default_value="false")
    enable_wrist_cam_arg = DeclareLaunchArgument("enable_wrist_cam", default_value="false")

    return LaunchDescription(
            [
                use_sim_arg,
                sim_gazebo_arg,
                cameras_config_arg,
                namespace_arg,
                enable_static_cam_arg,
                enable_wrist_cam_arg,
                # SetParameter(name="use_sim_time", value=use_sim),
                OpaqueFunction(function = spawn_cameras),
            ]
        )