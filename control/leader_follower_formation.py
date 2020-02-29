#!/usr/bin/python
# -*- coding: UTF-8 -*-
import rospy
from geometry_msgs.msg import Twist,Pose,PoseStamped,TwistStamped,Point
from std_msgs.msg import String
import sys 
Kp = 0.15
uav_num = int(sys.argv[1])
leader_id = 5
vision_pose = [None]*(uav_num+1)
relative_pose = [None]*(uav_num+1)
follower_vel_enu_pub = [None]*(uav_num+1)
relative_pose_pub = [None]*(uav_num+1)
follower_cmd_vel = [None]*(uav_num+1)
leader_cmd_vel = TwistStamped()

for i in range(uav_num):
    vision_pose[i+1]=PoseStamped()
    relative_pose[i+1]=PoseStamped()
    follower_cmd_vel[i+1]=Twist()

#    uav_5 is the leader in the formation mission
formation=[None]*10

formation_temp = [None]*(uav_num+1)               
for i in range(uav_num):                           
    if i+1 <= (uav_num/2):   
        if (i+1)%2 == 1£º                          
            formation_temp[i+1] = Point(0,i)
        else:
            formation_temp[i+1] = Point(0,-i-1)    #  2x5 formation
    else:                                          #  f f l f f
        if (i+1)%2 == 1£º                          #  f f f f f 
            formation_temp[i+1] = Point( -2, 1+i-(uav_num/2) )
        else:
            formation_temp[i+1] = Point( -2, (uav_num/2)-i+2 ) 
formation[0] = formation_temp


formation_temp = [None]*(uav_num+1)         #  2x5 formation
for i in range(uav_num):                    #   
    if (i+1)%2 == 1£º                       #  l f f f f 
        formation_temp[i+1] = Point(0,i)    #  f
    elif i+1 != uav_num:                    #  f   
        formation_temp[i+1] = Point(-i,0)   #  f
    else:                                   #  f       f
        formation_temp[i+1] = Point(-4,4)
formation[1] = formation_temp               


formation_temp = [None]*(uav_num+1)         #  formation
formation_temp[1]=Point(0,0)
formation_temp[2]=Point(-2,-2)£»formation_temp[3]=Point(-2,2)
formation_temp[4]=Point(-4,-4)£»formation_temp[5]=Point(-4,0)£»formation_temp[7]=Point(-4,4)
formation_temp[10]=Point(-6,-6)£»formation_temp[8]=Point(-6,-2)£»formation_temp[6]=Point(-6,2)£»formation_temp[2]=Point(-6,6)
formation[2] = formation_temp      

    


'''
formation.append( [[-1,-1],[0,-1],[1,-1],[-1,0],[0,0],[0,1]] )  #2x3 formation  
                                                              #  f l f 
                                                              #  f f f
formation.append(  [[-2,-2],[0,-2],[2,-2],[-1,-1],[0,0],[1,-1]] )#Trianglar formation
                                                              #     l
                                                              #    f  f
                                                              #   f  f  f
formation.append( [[0,-4],[0,-2],[0,-6],[-2,0],[0,0],[2,0]]  )  #'T' formation
                                                              #    f l f
                                                              #      f
                                                              #      f
                                                              #      f
formation_id = int(sys.argv[2])
'''

def leader_cmd_vel_callback(msg):
    global leader_cmd_vel
    leader_cmd_vel = msg

def calculate_relative_pose(uav_id):
    global relative_pose
    relative_pose[uav_id].pose.position.x = vision_pose[uav_id].pose.position.x - vision_pose[leader_id].pose.position.x
    relative_pose[uav_id].pose.position.y = vision_pose[uav_id].pose.position.y - vision_pose[leader_id].pose.position.y
    relative_pose[uav_id].pose.position.z = vision_pose[uav_id].pose.position.z - vision_pose[leader_id].pose.position.z

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

leader_cmd_vel_sub = rospy.Subscriber("/uav"+str(leader_id)+"/mavros/setpoint_velocity/cmd_vel", TwistStamped, leader_cmd_vel_callback)
formation_switch_sub = rospy.Subscriber("/xtdrone"+"/uav"+str(leader_id)+"/cmd",String, cmd_callback)

for i in range(uav_num):
    uav_id = i+1
    if uav_id != leader_id:
        follower_vel_enu_pub[i+1] = rospy.Publisher(
         '/xtdrone/uav'+str(i+1)+'/cmd_vel_enu', Twist, queue_size=10)

rate = rospy.Rate(100)
while(1):
    for i in range(uav_num):
        uav_id = i+1
        if uav_id != leader_id:
            follower_cmd_vel[uav_id].linear.x = (leader_cmd_vel.twist.linear.x+Kp*(formation[formation_id][uav_id].x- relative_pose[uav_id].pose.position.x) ) 
            follower_cmd_vel[uav_id].linear.y = (leader_cmd_vel.twist.linear.y+Kp*(formation[formation_id][uav_id].y- relative_pose[uav_id].pose.position.y) )
            follower_cmd_vel[uav_id].linear.z = leader_cmd_vel.twist.linear.z
            follower_cmd_vel[uav_id].angular.x = 0.0; follower_cmd_vel[uav_id].angular.y = 0.0;  follower_cmd_vel[uav_id].angular.z = 0.0
            follower_vel_enu_pub[uav_id].publish(follower_cmd_vel[uav_id])
    rate.sleep()
