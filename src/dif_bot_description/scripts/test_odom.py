#!/usr/bin/env python3
"""Uso: python3 test_odom.py forward  (avanza 1 m segun /odom)
      python3 test_odom.py spin     (gira 360 grados segun /odom)"""
import math
import sys

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


class OdomTest(Node):
    def __init__(self, mode):
        super().__init__("odom_test")
        self.mode = mode
        self.pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.create_subscription(Odometry, "/odom", self.on_odom, 10)
        self.start = None
        self.last_yaw = 0.0
        self.turned = 0.0
        self.stop_msgs = 0
        self.target = math.radians(float(sys.argv[2])) if len(sys.argv) > 2 else 2 * math.pi
        self.finished = False

    def on_odom(self, msg):
        p = msg.pose.pose.position
        yaw = yaw_of(msg.pose.pose.orientation)
        if self.start is None:
            self.start = (p.x, p.y)
            self.last_yaw = yaw
        self.turned += math.atan2(math.sin(yaw - self.last_yaw),
                                  math.cos(yaw - self.last_yaw))
        self.last_yaw = yaw
        dist = math.hypot(p.x - self.start[0], p.y - self.start[1])

        cmd = Twist()
        if self.mode == "forward" and dist < 1.0:
            cmd.linear.x = 0.2
        elif self.mode == "spin" and abs(self.turned) < self.target:
            cmd.angular.z = 0.5
        else:
            if self.stop_msgs == 0:
                print(f"odom: distancia = {dist:.3f} m, "
                      f"giro = {math.degrees(self.turned):.1f} grados")
            self.stop_msgs += 1
            if self.stop_msgs >= 5:
                self.finished = True
        self.pub.publish(cmd)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "forward"
    rclpy.init()
    node = OdomTest(mode)
    try:
        while rclpy.ok() and not node.finished:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    node.pub.publish(Twist())
    rclpy.spin_once(node, timeout_sec=0.2)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
