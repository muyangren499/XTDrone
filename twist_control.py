import rospy
from geometry_msgs.msg import Twist
import sys, select, os
if os.name == 'nt':
  import msvcrt
else:
  import tty, termios

MAX_LIN_VEL = 0.26
MAX_ANG_VEL = 0.3

LIN_VEL_STEP_SIZE = 0.02
ANG_VEL_STEP_SIZE = 0.05

msg = """
Control Your UTDrone!
---------------------------
Moving around:
        w
   a    s    d
        x

w/x : increase/decrease x linear velocity (-0.26 ~ 0.26)
a/d : increase/decrease y linear velocity (-0.26 ~ 0.26)

space key, s : force stop

CTRL-C to quit
"""

e = """
Communications Failed
"""

def getKey():
    if os.name == 'nt':
      return msvcrt.getch()

    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def vels(x_target_linear_vel, y_target_linear_vel):
    return "currently:\tx linear velocity %s\t y linear velocity %s " % (x_target_linear_vel,y_target_linear_vel)

def constrain(input, low, high):
    if input < low:
      input = low
    elif input > high:
      input = high
    else:
      input = input

    return input

def checkLinearLimitVelocity(vel):
    vel = constrain(vel, -MAX_LIN_VEL, MAX_LIN_VEL)

    return vel

def checkAngularLimitVelocity(vel):
    if turtlebot3_model == "burger":
      vel = constrain(vel, -BURGER_MAX_ANG_VEL, BURGER_MAX_ANG_VEL)
    elif turtlebot3_model == "waffle" or turtlebot3_model == "waffle_pi":
      vel = constrain(vel, -WAFFLE_MAX_ANG_VEL, WAFFLE_MAX_ANG_VEL)
    else:
      vel = constrain(vel, -BURGER_MAX_ANG_VEL, BURGER_MAX_ANG_VEL)

    return vel

if __name__=="__main__":
    if os.name != 'nt':
        settings = termios.tcgetattr(sys.stdin)

    rospy.init_node('UTDrone_twist_control')
    pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)

    status = 0
    x_target_linear_vel   = 0.0
    y_target_linear_vel   = 0.0

    try:
        print(msg)
        while(1):
            key = getKey()
            if key == 'w' :
                x_target_linear_vel = checkLinearLimitVelocity(x_target_linear_vel + LIN_VEL_STEP_SIZE)
                status = status + 1
                print(vels(x_target_linear_vel,y_target_linear_vel))
            elif key == 'x' :
                x_target_linear_vel = checkLinearLimitVelocity(x_target_linear_vel - LIN_VEL_STEP_SIZE)
                status = status + 1
                print(vels(x_target_linear_vel,y_target_linear_vel))
            elif key == 'a' :
                y_target_linear_vel = checkLinearLimitVelocity(y_target_linear_vel + LINE_VEL_STEP_SIZE)
                status = status + 1
                print(vels(x_target_linear_vel,y_target_linear_vel))
            elif key == 'd' :
                y_target_linear_vel = checkLinearLimitVelocity(y_target_linear_vel - LINE_VEL_STEP_SIZE)
                status = status + 1
                print(vels(x_target_linear_vel,y_target_linear_vel))
            elif key == ' ' or key == 's' :
                x_target_linear_vel   = 0.0
                y_target_linear_vel  = 0.0
                print(vels(x_target_linear_vel, y_target_linear_vel))
            else:
                if (key == '\x03'):
                    break

            if status == 20 :
                print(msg)
                status = 0

            twist = Twist()

            twist.linear.x = x_target_linear_vel; twist.linear.y = y_target_linear_vel; twist.linear.z = 0.0
            twist.angular.x = 0.0; twist.angular.y = 0.0; twist.angular.z = 0.0

            pub.publish(twist)

    except:
        print(e)

    finally:
        twist = Twist()
        twist.linear.x = 0.0; twist.linear.y = 0.0; twist.linear.z = 0.0
        twist.angular.x = 0.0; twist.angular.y = 0.0; twist.angular.z = 0.0
        pub.publish(twist)

    if os.name != 'nt':
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
