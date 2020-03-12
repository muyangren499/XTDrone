import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D   
import matplotlib.animation as animation              
import numpy as np 
import rospy
from geometry_msgs.msg import Twist,Pose,PoseStamped,TwistStamped
from gazebo_msgs.srv import GetModelState

use_1_8 = 1


#uav_num = int(sys.argv[1])
uav_num=6
step_time=0.05

pose_puber=[None]*uav_num

plot_x=[0]*(uav_num)
plot_y=[0]*(uav_num)
plot_z=[0]*(uav_num)

for i in range(uav_num):
    uav_id=i+use_1_8
    plot_x[i]= i//3
    plot_y[i]= i%3
    pose_puber[i]=rospy.Publisher('/uav'+str(uav_id)+'/mavros/local_pose/pose', PoseStamped, queue_size=10)

# def pose_pub():
#     for i in range(uav_num):
#         msg=PoseStamped()
#         msg.pose.position.x=plot_x[i]
#         msg.pose.position.y=plot_y[i]
#         msg.pose.position.z=plot_z[i]
#         pose_puber[i].publish(msg)

fig = plt.figure()
plt.ion()
ax = Axes3D(fig)
label_lim = 20

def scroll_call_back(event):
    global label_lim
    if event.button == 'up':
        label_lim+=2
        print('up')
    elif event.button == 'down':
        label_lim=label_lim-2 if label_lim>10 else 10
        print('down')


fig.canvas.mpl_connect('scroll_event', scroll_call_back)

def init():
    ax.set_xlim3d(-label_lim, label_lim)
    ax.set_ylim3d(-label_lim, label_lim)
    ax.set_zlim3d(-1,200)


def cmd_vel_callback(msg,id):
    vel=msg
    plot_x[id]+=step_time*vel.linear.x
    plot_y[id]+=step_time*vel.linear.y
    plot_z[id]+=step_time*vel.linear.z
    local_pose=PoseStamped()
    local_pose.pose.position.x=plot_x[id]
    local_pose.pose.position.y=plot_y[id]
    local_pose.pose.position.z=plot_z[id]    
    pose_puber[id].publish(local_pose)

rospy.init_node('simple_3d_simulator')
rate = rospy.Rate(100)

for i in range(uav_num):
    uav_id=i+use_1_8
    rospy.Subscriber('/xtdrone/uav'+str(uav_id)+'/cmd_vel_flu', Twist, cmd_vel_callback,i) 
    rospy.Subscriber('/xtdrone/uav'+str(uav_id)+'/cmd_vel_enu', Twist, cmd_vel_callback,i)    

# def get_odom(id):
#     try:
#         handle = rospy.ServiceProxy('gazebo/get_model_state',GetModelState)
#         response = handle('iris_'+str(id),'ground_plane')
#         return response
#     except rospy.ServiceException,e:
#         print "Service call failed: %s"%e



try:
    while 1:
        # for i in range(uav_num):
        #     uav_id=i
        #     true_pose = get_odom(uav_id)
        #     plot_x[uav_id]=true_pose.pose.position.x
        #     plot_y[uav_id]=true_pose.pose.position.y
        #     plot_z[uav_id]=true_pose.pose.position.z
        init()
        ax.scatter(plot_x,plot_y,plot_z,marker="x")
        plt.pause(step_time)
        ax.cla()
        rate.sleep()
except KeyboardInterrupt:
        plt.ioff()