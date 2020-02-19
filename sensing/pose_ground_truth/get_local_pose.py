import rospy
from gazebo_msgs.srv import GetModelState
from geometry_msgs.msg import PoseStamped
def get_odom():
    try:
        handle = rospy.ServiceProxy('gazebo/get_model_state',GetModelState)
        response = handle('iris_lidar','ground_plane')
        return response
    except rospy.ServiceException, e:
        print "Service call failed: %s"%e

if __name__ == '__main__':
    rospy.init_node('get_pose_groundtruth')
    pose_pub = rospy.Publisher("/mavros/vision_pose/pose", PoseStamped, queue_size=2)
    local_pose = PoseStamped()
    local_pose.header.frame_id = 'map'
    rate = rospy.Rate(100)
    while True:
        odom= get_odom()
        local_pose.header.stamp = rospy.Time.now()
        local_pose.pose = odom.pose
        pose_pub.publish(local_pose)
        rate.sleep()

