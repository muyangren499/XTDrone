#!/usr/bin/python
# -*- coding: UTF-8 -*-
import rospy
from geometry_msgs.msg import Twist,Pose,PoseStamped,TwistStamped
from std_msgs.msg import String
import sys 
import time
KP_xy = 1
KP_z = 1.5
max_vel_xy = 1
max_vel_z = 0.6
uav_num = int(sys.argv[1])
leader_id = 5
vision_pose = [None]*(uav_num+1)
relative_pose = [None]*(uav_num+1)
follower_vel_enu_pub = [None]*(uav_num+1)
relative_pose_pub = [None]*(uav_num+1)
follower_cmd_vel = [None]*(uav_num+1)
leader_cmd_vel = Twist()
avoid_vel_z = [0]*(uav_num+1)
avoid_pos_z = 0.3
leader_height = 0
hover = True
avoid = False

for i in range(uav_num):
    vision_pose[i+1]=PoseStamped()
    relative_pose[i+1]=PoseStamped()
    follower_cmd_vel[i+1]=Twist()

formation=[]
formation.append( [[-1,-1],[0,-1],[1,-1],[-1,0],[0,0],[0,1]] )  #2x3 formation
                                                              #  i i i 
                                                              #  i i i
formation.append(  [[-2,-2],[0,-2],[2,-2],[-1,-1],[0,0],[1,-1]] )#Trianglar formation
                                                              #     i
                                                              #    i  i
                                                              #   i  i  i
formation.append( [[0,-4],[0,-2],[0,-6],[-2,0],[0,0],[2,0]]  )  #'T' formation
                                                              #    i i i
                                                              #      i
                                                              #      i
                                                              #      i
formation_id = 0


def leader_cmd_vel_callback(msg):
    global leader_cmd_vel
    leader_cmd_vel = msg
    if msg.linear.z == 0:
        hover = True
    else:
        hove = False

def calculate_relative_pose(uav_id):
    global relative_pose
    relative_pose[uav_id].pose.position.x = vision_pose[uav_id].pose.position.x - vision_pose[leader_id].pose.position.x
    relative_pose[uav_id].pose.position.y = vision_pose[uav_id].pose.position.y - vision_pose[leader_id].pose.position.y
    relative_pose[uav_id].pose.position.z = vision_pose[uav_id].pose.position.z - vision_pose[leader_id].pose.position.z

def delta_vel(target_pos, current_pos, KP, vel_max):
    delta_vel = KP*(target_pos-current_pos)
    if delta_vel > vel_max:
        delta_vel = vel_max
    return delta_vel

vision_pose_callback = [None]*(uav_num+1)

rospy.init_node('formation_control')


def vision_pose_callback(msg,id):
    global vision_pose
    vision_pose[id] = msg 
    calculate_relative_pose(id)

def cmd_callback(msg):
    global formation_id
    if not msg.data == '': 
        formation_id = int(msg.data[-1])
        print("Switch to Formation"+str(formation_id))

for i in range(uav_num):
    uav_id = i+1
    rospy.Subscriber("/uav"+str(uav_id)+"/mavros/vision_pose/pose", PoseStamped , vision_pose_callback,uav_id)

leader_cmd_vel_sub = rospy.Subscriber("/xtdrone/leader_cmd_vel", Twist, leader_cmd_vel_callback)
formation_switch_sub = rospy.Subscriber("/xtdrone/leader_cmd",String, cmd_callback)
leader_vel_enu_pub =  rospy.Publisher('/xtdrone/uav'+str(leader_id)+'/cmd_vel_enu', Twist, queue_size=10)
for i in range(uav_num):
    uav_id = i+1
    if uav_id != leader_id:
        follower_vel_enu_pub[uav_id] = rospy.Publisher(
         '/xtdrone/uav'+str(uav_id)+'/cmd_vel_enu', Twist, queue_size=10)
leader_height = vision_pose[leader_id].pose.position.z 
#print("recording original height...")
#time.sleep(2)
#print(str(leader_height)+'m')
rate = rospy.Rate(100)
while(1):
    # Avoid collision with other drones 
    for i in range(uav_num): 
        uav_id = i+1      
        for j in range(1,uav_num-i):            
            if pow(vision_pose[uav_id].pose.position.x-vision_pose[uav_id+j].pose.position.x,2)\
                +pow(vision_pose[uav_id].pose.position.y-vision_pose[uav_id+j].pose.position.y,2)\
                 +pow(vision_pose[uav_id].pose.position.z-vision_pose[uav_id+j].pose.position.z,2)  < 0.6:
                avoid = True
                avoid_vel_z[uav_id] = KP_z*avoid_pos_z
                avoid_vel_z[uav_id+j] = -KP_z*avoid_pos_z
            else:
                avoid_vel_z[uav_id] = 0
                avoid_vel_z[uav_id+j] = 0
    for i in range(uav_num):
        uav_id = i+1
        if uav_id != leader_id:
            follower_cmd_vel[uav_id].linear.x = leader_cmd_vel.linear.x+delta_vel(formation[formation_id][i][0],relative_pose[uav_id].pose.position.x,KP_xy, max_vel_xy) 
            follower_cmd_vel[uav_id].linear.y = leader_cmd_vel.linear.y+delta_vel(formation[formation_id][i][1],relative_pose[uav_id].pose.position.y, KP_xy, max_vel_xy) 
            follower_cmd_vel[uav_id].linear.z = leader_cmd_vel.linear.z + delta_vel(leader_height,vision_pose[uav_id].pose.position.z, KP_z, max_vel_z) + avoid_vel_z[uav_id] - avoid_vel_z[leader_id]

            follower_cmd_vel[uav_id].angular.x = 0.0; follower_cmd_vel[uav_id].angular.y = 0.0; follower_cmd_vel[uav_id].angular.z = leader_cmd_vel.angular.z
            
            follower_vel_enu_pub[uav_id].publish(follower_cmd_vel[uav_id])

    if hover: 
        leader_cmd_vel.linear.z = delta_vel(leader_height,vision_pose[leader_id].pose.position.z, KP_z, max_vel_z) + avoid_vel_z[leader_id]
    else:
        leader_cmd_vel.linear.z = leader_cmd_vel.linear.z + avoid_vel_z[leader_id]
        if not avoid:
            leader_height = vision_pose[leader_id].pose.position.z
    leader_vel_enu_pub.publish(leader_cmd_vel)

    rate.sleep()
