#!/usr/bin/env python
"""Node to run the racersim with ROS bindings.

License:
  BSD 3-Clause License
  Copyright (c) 2020, Autonomous Robotics Club of Purdue (Purdue ARC)
  All rights reserved.
  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions are met:
  1. Redistributions of source code must retain the above copyright notice, this
     list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright notice,
     this list of conditions and the following disclaimer in the documentation
     and/or other materials provided with the distribution.
  3. Neither the name of the copyright holder nor the names of its
     contributors may be used to endorse or promote products derived from
     this software without specific prior written permission.
  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
  OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

# 3rd party modules
from threading import Lock
import rospy
from geometry_msgs.msg import Twist, PoseWithCovarianceStamped
from nav_msgs.msg import Odometry
from std_srvs.srv import Empty, EmptyResponse

# Local library
import racersim

class RacerSimROS(object):
    """ROS wrapper for the racer sim."""
    def __init__(self):
        rospy.init_node('sim_node')

        self.sim = racersim.Sim(
            renderEnabled=rospy.get_param('~render/enabled', True),
            velIters=rospy.get_param('~render/velIters', 6),
            posIters=rospy.get_param('~render/posIters', 2),
            bounds=rospy.get_param('~world/bounds', 1.5),
            scaling=rospy.get_param('~render/scaling', 500)
        )

        self.lock = Lock()
        self.last_command = None
        self.last_time = None

        self.frame_id = rospy.get_param('~frame_id', 'sim')
        self.timeout = rospy.get_param('~timeout', 1.0) # Seconds
        rate = rospy.Rate(rospy.get_param('~rate', 30)) # Hz

        # Publishers
        self.ball_pub = rospy.Publisher('ball_pose', \
             PoseWithCovarianceStamped, queue_size=3)
        self.bot_pub = rospy.Publisher('bot_odom', Odometry, queue_size=3)
        self.goal_pub = rospy.Publisher('goal_pose', \
             PoseWithCovarianceStamped, queue_size=3)

        # Subscribers
        rospy.Subscriber('bot_velocity_command', Twist, self.command_cb)

        while not rospy.is_shutdown():
            self.loop_once()
            try:
                rate.sleep()
            except rospy.ROSInterruptException:
                pass

    def command_cb(self, command_msg):
        """Callback for command messages for snake."""
        # Put this all in one tuple so that it is atomic
        self.last_command = (rospy.Time.now(), command_msg.linear.x, command_msg.angular.z)

    def loop_once(self):
        """Main loop."""
        self.lock.acquire()
        now = rospy.Time.now()

        if self.last_time is not None:
            # iterate game one step
            if self.last_command is not None:
                delta_t = (now - self.last_time).to_sec()
                last_command_time, linear, angular = self.last_command
                if (now - last_command_time).to_sec() >= self.timeout:
                    self.sim.step(0.0, 0.0, delta_t)
                else:
                    self.sim.step(linear, angular, delta_t)

            # Publish ball pose with covariance and stamp
            ball_msg = PoseWithCovarianceStamped()
            ball_msg.header.stamp = now
            ball_msg.frame_id = self.frame_id
            ball_point = self.sim.ball.getPoint()
            ball_msg.pose.pose.position.x = ball_point[0]
            ball_msg.pose.pose.position.y = ball_point[1]
            self.ball_pub.publish(ball_msg)

            # Publish bot odometry
            bot_msg = Odometry()
            bot_msg.header.stamp = now
            bot_msg.header.frame_id = self.frame_id
            bot_point = self.sim.car.getPoint()
            bot_msg.pose.pose.position.x = bot_point[0]
            bot_msg.pose.pose.position.y = bot_point[1]
            bot_quat = self.sim.car.getQuaternion()
            bot_msg.pose.pose.orientation.w = bot_quat[0]
            bot_msg.pose.pose.orientation.z = bot_quat[3]
            linear = self.sim.car.body.linearVelocity
            bot_msg.twist.twist.linear.x = linear[0]
            bot_msg.twist.twist.linear.y = linear[1]
            angular = self.sim.car.body.angularVelocity
            bot_msg.twist.twist.angular.x = angular[0]
            bot_msg.twist.twist.angular.y = angular[1]
            self.bot_pub.publish(bot_msg)

            # Publish goal pose with covariance and stamp
            goal_msg = PoseWithCovarianceStamped()
            goal_msg.header.stamp = now
            goal_msg.frame_id = self.frame_id
            goal_msg = self.sim.goal.getPoint()
            goal_msg.pose.pose.position.x = goal_msg[0]
            goal_msg.pose.pose.position.y = goal_msg[1]
            self.ball_pub.publish(goal_msg)

        self.last_time = now
        self.lock.release()

if __name__ == "__main__":
    RacerSimROS()