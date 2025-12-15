import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace
from ros_gz_bridge.actions import RosGzBridge
from ros_gz_sim.actions import GzServer


def generate_launch_description():
    pkg_share = get_package_share_directory('sam_bot_description')
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')
    gz_spawn_model_launch_source = os.path.join(ros_gz_sim_share, "launch", "gz_spawn_model.launch.py")
    default_model_path = os.path.join(pkg_share, 'src', 'description', 'sam_bot_description.sdf')
    new_model_path = os.path.join(pkg_share, 'src', 'description', 'sam_bot_description_2.sdf')
    default_rviz_config_path = os.path.join(pkg_share, 'rviz', 'config.rviz')
    world_path = os.path.join(pkg_share, 'world', 'my_world.sdf')
    bridge_config_path = os.path.join(pkg_share, 'config', 'bridge_config.yaml')
    nb_robots = 2

    robot_state_publisher_node_0 = Node(
        namespace='r0',
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': Command(['xacro ', LaunchConfiguration('model')])}, {'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )
    robot_state_publisher_node_1 = Node(
        namespace='r1',
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': Command(['xacro ', LaunchConfiguration('new_model')])}, {'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rvizconfig')],
    )
    gz_server = GzServer(
        world_sdf_file=world_path,
        container_name='ros_gz_container',
        create_own_container='True',
        use_composition='True',
    )
    ros_gz_bridge = RosGzBridge(
        bridge_name='ros_gz_bridge',
        config_file=bridge_config_path,
        container_name='ros_gz_container',
        create_own_container='False',
        use_composition='True',
    )
    # camera_bridge_image = Node(
    #     package='ros_gz_image',
    #     executable='image_bridge',
    #     name='bridge_gz_ros_camera_image',
    #     output='screen',
    #     parameters=[{'use_sim_time': True}],
    #     arguments=['/depth_camera/image'],
    # )
    # camera_bridge_depth = Node(
    #     package='ros_gz_image',
    #     executable='image_bridge',
    #     name='bridge_gz_ros_camera_depth',
    #     output='screen',
    #     parameters=[{'use_sim_time': True}],
    #     arguments=['/depth_camera/depth_image'],
    # )
    spawn_entity_0 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gz_spawn_model_launch_source),
        launch_arguments={
            'world': 'my_world',
            'topic': '/r0/robot_description',
            'entity_name': 'sam_bot_0',
            'x': '0.00',
            'y': '0.00',
            'z': '0.65',
        }.items(),
    )
    spawn_entity_1 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gz_spawn_model_launch_source),
        launch_arguments={
            'world': 'my_world',
            'topic': '/r1/robot_description',
            'entity_name': 'sam_bot_1',
            'x': '-6.00',
            'y': '-4.00',
            'z': '0.65',
            'roll': '1.57', 
        }.items(),
    )
    robot_localization_node_1 = Node(
        namespace='r0',
        package='robot_localization',
        executable='ekf_node',
        name='ekf_node',
        output='screen',
        parameters=[os.path.join(pkg_share, 'config/ekf.yaml'), {'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )
    robot_localization_node_2 = Node(
        namespace='r1',
        package='robot_localization',
        executable='ekf_node',
        name='ekf_node',
        output='screen',
        parameters=[os.path.join(pkg_share, 'config/ekf2.yaml'), {'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )
    


    return LaunchDescription([
        DeclareLaunchArgument(name='model', default_value=default_model_path, description='Absolute path to robot model file'),
        DeclareLaunchArgument(name='new_model', default_value=new_model_path, description='Absolute path to new robot model file'),
        DeclareLaunchArgument(name='rvizconfig', default_value=default_rviz_config_path, description='Absolute path to rviz config file'),
        DeclareLaunchArgument(name='use_sim_time', default_value='True', description='Flag to enable use_sim_time'),
        ExecuteProcess(cmd=['gz', 'sim', '-g'], output='screen'),
        robot_state_publisher_node_0,
        robot_state_publisher_node_1,
        rviz_node,
        gz_server,
        ros_gz_bridge,
        # camera_bridge_image,
        # camera_bridge_depth,
        spawn_entity_0,
        spawn_entity_1,
        robot_localization_node_1,
        robot_localization_node_2
    ])
