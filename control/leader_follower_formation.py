import rospy
from geometry_msgs.msg import Twist,Pose,PoseStamped,TwistStamped
Kp = 0.01
uav_num = 5
vision_pose = [PoseStamped()]*(uav_num+1)
relative_pose = [PoseStamped()]*(uav_num+1)
follower_vel_flu_pub = [None]*(uav_num+1)
leader_id = 5
leader_cmd_vel = TwistStamped()
follower_cmd_vel = [Twist()]*(uav_num+1)

formation=[]
formation.append( [[-1,-1],[0,-1],[1,-1],[-1,0],[0,0],[0,1]] )  #2x3 formation
                                                              #  i i i 
                                                              #  i i i
formation.append(  [[-2,-2],[0,-2],[2,-2],[-1,-1],[0,0],[1,-1]] )#Trianglar formation
                                                              #     i
                                                              #    i  i
                                                              #   i  i  i
formation.append( [[0,-2],[0,-1],[0,-3],[-1,0],[0,0],[1,0]]  )  #'T' formation
                                                              #    i i i
                                                              #      i
                                                              #      i
                                                              #      i
formation_id = 0


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

for i in range(uav_num):
    uav_id = i+1
    def func(msg):
        global vision_pose
        vision_pose[uav_id] = msg
        calculate_relative_pose(uav_id)
    vision_pose_callback[uav_id] = func

for i in range(uav_num):
    uav_id = i+1
    rospy.Subscriber("/uav"+str(uav_id)+"/mavros/vision_pose/pose", PoseStamped , vision_pose_callback[uav_id] )

leader_cmd_vel_sub = rospy.Subscriber("/uav"+str(leader_id)+"/mavros/setpoint_velocity/cmd_vel", TwistStamped, leader_cmd_vel_callback)


for i in range(uav_num):
    uav_id = i+1
    if uav_id != leader_id:
        follower_vel_flu_pub[i+1] = rospy.Publisher(
         '/xtdrone/uav'+str(i+1)+'/cmd_vel_enu', Twist, queue_size=10)

while(1):
    for i in range(uav_num):
        uav_id = i+1
        if uav_id != leader_id:
            follower_cmd_vel[uav_id].linear.x = (leader_cmd_vel.twist.linear.x+Kp*(formation[formation_id][i][0]- relative_pose[uav_id].pose.position.x) ) 
            follower_cmd_vel[uav_id].linear.y = (leader_cmd_vel.twist.linear.y+Kp*(formation[formation_id][i][1]- relative_pose[uav_id].pose.position.y) )
            follower_cmd_vel[uav_id].linear.z = leader_cmd_vel.twist.linear.z
            follower_cmd_vel[uav_id].angular.x = 0.0; follower_cmd_vel[uav_id].angular.y = 0.0;  follower_cmd_vel[uav_id].angular.z = 0.0
            follower_vel_flu_pub[uav_id].publish(follower_cmd_vel[uav_id])