#!/usr/bin/env python3
"""Uso: python3 latency_test.py --ros-args -p use_sim_time:=true"""
import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node


class Latency(Node):
    def __init__(self):
        super().__init__("latency_test")
        self.pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.create_subscription(Odometry, "/odom", self.on_odom, 10)
        self.v = None
        self.phase = "wait"
        self.t0 = self.t1 = self.t2 = 0.0
        self.zeros = 0
        self.done = False
        self.create_timer(0.05, self.tick)

    def now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def on_odom(self, msg):
        self.v = msg.twist.twist.linear.x
        if self.phase == "go" and abs(self.v) > 0.1:
            print(f"Latencia de arranque (|v| > 0.1 m/s): {self.now() - self.t0:.3f} s de simulacion")
            self.phase = "run"
            self.t1 = self.now()

    def tick(self):
        t = self.now()
        cmd = Twist()
        if self.phase == "wait":
            if self.t0 == 0.0:
                self.t0 = t
            if self.v is not None and abs(self.v) < 0.02 and t - self.t0 > 1.0:
                self.phase = "go"
                self.t0 = t
        elif self.phase in ("go", "run"):
            cmd.linear.x = 0.2
            self.pub.publish(cmd)
            if self.phase == "run" and t - self.t1 > 2.0:
                self.phase = "cut"
                self.t2 = t
        elif self.phase == "cut":
            if abs(self.v) < 0.02:
                print(f"Al cortar el comando: se detuvo solo en {t - self.t2:.2f} s de simulacion")
                self.phase = "end"
            elif t - self.t2 > 3.0:
                print(f"Al cortar el comando: NO se detuvo solo (sigue a {self.v:.2f} m/s)")
                self.phase = "end"
        elif self.phase == "end":
            self.pub.publish(cmd)
            self.zeros += 1
            if self.zeros >= 10:
                self.done = True


def main():
    rclpy.init()
    node = Latency()
    try:
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    node.pub.publish(Twist())
    rclpy.spin_once(node, timeout_sec=0.2)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
