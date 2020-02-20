# XTDrone

#### 介绍
这是基于PX4和ROS的无人机仿真平台，在这个平台上，开发者可以快速验证算法。如：
1. 目标检测与追踪
   
2. 视觉SLAM
   
3. 激光SLAM

4. VIO 
   
5. 运动规划
   
6. 多机协同

#### 软件架构
- 通信:PX4与ROS之间的通信封装进Python类
- 控制：键盘控制无人机速度和偏航转速
- 感知
  1. 目标检测与追踪
       - YOLO
  2. SLAM：
     1. VSLAM: 
         - ORBSLAM2
     2. Laser_SLAM:
         - PLICP+gmapping
     3. VIO
         - VINS-Mono（仿真平台起飞前初始化问题有待解决）
  3. 位姿真值获取
  4. 语音识别（待开发）
- 运动规划(目前只有二维)
  1. 全局规划
      - A*
      - Dijkstra
  2. 局部规划
      - DWA
- 协同：可以实现任意多架飞机的同时控制，只有简单编队demo，仍需继续开发
- 仿真配置
  1. 无人机PX4参数
     - 可拒止GPS和磁罗盘
  2. 启动脚本
  3. Gazebo模型
     - 支持双目相机、深度相机、单线雷达和多线雷达 
  4. Gazebo世界
     - 一个户外场景（有车辆和移动的行人）
     - 三个室内场景


#### 安装教程

1.  xxxx
2.  xxxx
3.  xxxx

#### 使用说明

1.  xxxx
2.  xxxx
3.  xxxx

#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request
