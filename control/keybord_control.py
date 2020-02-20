#!/usr/bin/env python

# Copyright (c) 2011, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Willow Garage, Inc. nor the names of its
#      contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import rospy
from geometry_msgs.msg import Twist
import sys, select, os
import tty, termios

MAX_LIN_VEL = 0.2
MAX_ANG_VEL = 0.1
LIN_VEL_STEP_SIZE = 0.02
ANG_VEL_STEP_SIZE = 0.01

msg = """
Control Your XTDrone!
---------------------------
Moving around:
        w               i
   a    s    d     j    k    l
        x               ,

w/x : increase/decrease forward velocity (-0.2~0.2)
a/d : increase/decrease leftward velocity (-0.2~0.2)
i/, : increase/decrease upward velocity (-0.2~0.2)
j/l : increase/decrease angular velocity (-0.1~0.1)

s or k : force stop

CTRL-C to quit
"""

e = """
Communications Failed
"""

def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def vels(target_forward_vel, target_leftward_vel, target_upward_vel,target_angular_vel):
    return "currently:\t forward x %s\t leftward y %s\t upward z %s\t angular %s " % (target_forward_vel, target_leftward_vel, target_upward_vel, target_angular_vel)

def makeSimpleProfile(output, input, slop):
    if input > output:
        output = min( input, output + slop )
    elif input < output:
        output = max( input, output - slop )
    else:
        output = input
    return output

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
    vel = constrain(vel, -MAX_ANG_VEL, MAX_ANG_VEL)
    return vel

if __name__=="__main__":
    settings = termios.tcgetattr(sys.stdin)

    rospy.init_node('keyboard_control')
    pub = rospy.Publisher('/xtdrone/cmd_vel_flu', Twist, queue_size=10)


    target_forward_vel   = 0.0
    target_leftward_vel   = 0.0
    target_upward_vel   = 0.0
    target_angular_vel  = 0.0
    control_forward_vel  = 0.0
    control_leftward_vel  = 0.0
    control_upward_vel  = 0.0
    control_angular_vel = 0.0

    try:
        print(msg)
        while(1):
            key = getKey()
            if key == 'w' :
                target_forward_vel = checkLinearLimitVelocity(target_forward_vel + LIN_VEL_STEP_SIZE)
                print(vels(target_forward_vel,target_leftward_vel,target_upward_vel,target_angular_vel))
            elif key == 'x' :
                target_forward_vel = checkLinearLimitVelocity(target_forward_vel - LIN_VEL_STEP_SIZE)
                print(vels(target_forward_vel,target_leftward_vel,target_upward_vel,target_angular_vel))
            elif key == 'a' :
                target_leftward_vel = checkLinearLimitVelocity(target_leftward_vel + LIN_VEL_STEP_SIZE)
                print(vels(target_forward_vel,target_leftward_vel,target_upward_vel,target_angular_vel))
            elif key == 'd' :
                target_leftward_vel = checkLinearLimitVelocity(target_leftward_vel - LIN_VEL_STEP_SIZE)
                print(vels(target_forward_vel,target_leftward_vel,target_upward_vel,target_angular_vel))
            elif key == 'i' :
                target_upward_vel = checkLinearLimitVelocity(target_upward_vel + LIN_VEL_STEP_SIZE)
                print(vels(target_forward_vel,target_leftward_vel,target_upward_vel,target_angular_vel))
            elif key == ',' :
                target_upward_vel = checkLinearLimitVelocity(target_upward_vel - LIN_VEL_STEP_SIZE)
                print(vels(target_forward_vel,target_leftward_vel,target_upward_vel,target_angular_vel))
            elif key == 'j':
                target_angular_vel = checkAngularLimitVelocity(target_angular_vel + ANG_VEL_STEP_SIZE)
                print(vels(target_forward_vel,target_leftward_vel,target_upward_vel,target_angular_vel))
            elif key == 'l':
                target_angular_vel = checkAngularLimitVelocity(target_angular_vel - ANG_VEL_STEP_SIZE)
                print(vels(target_forward_vel,target_leftward_vel,target_upward_vel,target_angular_vel))
            elif key == 's' or key == 'k' :
                target_forward_vel   = 0.0
                target_leftward_vel   = 0.0
                target_upward_vel   = 0.0
                target_angular_vel  = 0.0
                control_forward_vel  = 0.0
                control_leftward_vel  = 0.0
                control_upward_vel  = 0.0
                control_angular_vel = 0.0
                print(vels(target_forward_vel,-target_leftward_vel,target_upward_vel,target_angular_vel))
            else:
                if (key == '\x03'):
                    break

            twist = Twist()

            control_forward_vel = makeSimpleProfile(control_forward_vel, target_forward_vel, (LIN_VEL_STEP_SIZE/2.0))
            control_leftward_vel = makeSimpleProfile(control_leftward_vel, target_leftward_vel, (LIN_VEL_STEP_SIZE/2.0))
            control_upward_vel = makeSimpleProfile(control_upward_vel, target_upward_vel, (LIN_VEL_STEP_SIZE/2.0))
            twist.linear.x = control_forward_vel; twist.linear.y = control_leftward_vel; twist.linear.z = control_upward_vel

            control_angular_vel = makeSimpleProfile(control_angular_vel, target_angular_vel, (ANG_VEL_STEP_SIZE/2.0))
            twist.angular.x = 0.0; twist.angular.y = 0.0;  twist.angular.z = control_angular_vel

            pub.publish(twist)

    except:
        print(e)

    finally:
        twist = Twist()
        twist.linear.x = 0.0; twist.linear.y = 0.0; twist.linear.z = 0.0
        twist.angular.x = 0.0; twist.angular.y = 0.0; twist.angular.z = 0.0
        pub.publish(twist)

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
