#!/usr/bin/env python3
"""Convierte /cmd_vel (Twist) a /cmd_vel_stamped (TwistStamped) para diff_drive_controller."""
import rclpy
from geometry_msgs.msg import Twist, TwistStamped
from rclpy.node import Node


class TwistStamper(Node):
    def __init__(self):
        super().__init__("twist_stamper")
        self.pub = self.create_publisher(TwistStamped, "/cmd_vel_stamped", 10)
        self.create_subscription(Twist, "/cmd_vel", self.on_cmd, 10)

    def on_cmd(self, msg):
        out = TwistStamped()
        out.header.stamp = self.get_clock().now().to_msg()
        out.header.frame_id = "base_link"
        out.twist = msg
        self.pub.publish(out)


def main():
    rclpy.init()
    node = TwistStamper()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
