# XTDrone

<div id="sidebar"><a href="./README.md" target="_blank"><font color=#0000FF size=5px >[中文版]<font></center><a></div>
#### Description
This is a customizable Multi-Rotor UAVs simulation platform based on PX4 and ROS, on which developers can quickly verify algorithms. Such as:

1. Object Detection and Tracking
<img src="./gif/human_tracking.gif" width="640" height="368" /> 

2. Visual SLAM
<img src="./gif/vslam.gif" width="640" height="368" /> 

3. Laser Slam
<img src="./gif/laser_slam.gif" width="640" height="368" /> 

4. VIO 
<img src="./gif/vio.gif" width="640" height="368" />  

5. Motion Planning
<img src="./gif/motion_planning.gif" width="640" height="368" />  

6. Formation
<img src="./gif/cooperation.gif" width="640" height="368" />  

#### Software Architecture
- Comunication: The communication between PX4 and ROS is encapsulated in the Python class, and multi-machine communication starts multiple processes
- Control：Use the keyboard to switch drone flight modes, control unlocking, adjust speed and yaw steering
- Perception
  1. Object Detection and Tracking
       - YOLO
  2. SLAM：
     1. VSLAM: 
         - ORBSLAM2
     2. Laser_SLAM:
         - PLICP+gmapping
     3. VIO
         - VINS-Mono（pre-flight initialization issues need to be improved）
  3. Ground true pose acquisition
  4. Speech Recognition（to be developed）
- Motion Planning(currently only supports 2D )
  1. Global planning
      - A*
      - Dijkstra
  2. Local planning
      - DWA
- Collaboration：Multi-UAV Formation
- Simulation configuration
  1. PX4 configuration
     - Can reject GPS and magnetic compass
  2. Launch script
  3. Gazebo models
     - Stereo Camera、Depth Camera、LiDAR
  4. Gazebo worlds
     - 2 outdoor worlds
     - 3 indoor worlds


#### Installation

View the tutorial doc [XTDrone](https://www.yuque.com/qvdzhs/xtdrone_manual_en)

#### Contribution


1.  Fork the repository
2.  Create Feat_xxx branch
3.  Commit your code
4.  Create Pull Request
