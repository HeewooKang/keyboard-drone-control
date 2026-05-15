import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
import pygame


class RealtimeKeyboardDrone(Node):
    def __init__(self):
        super().__init__('keyboard_drone_realtime')

        self.pub = self.create_publisher(
            TwistStamped,
            '/mavros/setpoint_velocity/cmd_vel',
            10
        )

        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0
        self.wz = 0.0

        self.tx = 0.0
        self.ty = 0.0
        self.tz = 0.0
        self.twz = 0.0

        self.max_lin = 2
        self.max_ang = 2
        self.acc = 0.2

        pygame.init()
        pygame.display.set_caption("Keyboard Drone Control")
        self.screen = pygame.display.set_mode((760, 260))
        self.font = pygame.font.SysFont(None, 28)
        self.clock = pygame.time.Clock()

        self.get_logger().info(
            "Click window first!\n"
            "W/S: forward/back (BODY)\n"
            "A/D: left/right (BODY)\n"
            "Q/E: up/down\n"
            "J/K: yaw\n"
            "SPACE: stop\n"
            "ESC: quit"
        )

        self.timer = self.create_timer(0.02, self.control_loop)

    def smooth_step(self, current, target):
        return current + (target - current) * self.acc

    def read_keyboard(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt

        if not pygame.key.get_focused():
            self.tx = self.ty = self.tz = self.twz = 0.0
            return

        keys = pygame.key.get_pressed()

        self.tx = 0.0
        self.ty = 0.0
        self.tz = 0.0
        self.twz = 0.0

        if keys[pygame.K_w] and not keys[pygame.K_s]:
            self.tx = self.max_lin
        elif keys[pygame.K_s] and not keys[pygame.K_w]:
            self.tx = -self.max_lin

        if keys[pygame.K_a] and not keys[pygame.K_d]:
            self.ty = self.max_lin
        elif keys[pygame.K_d] and not keys[pygame.K_a]:
            self.ty = -self.max_lin

        if keys[pygame.K_q] and not keys[pygame.K_e]:
            self.tz = self.max_lin
        elif keys[pygame.K_e] and not keys[pygame.K_q]:
            self.tz = -self.max_lin

        if keys[pygame.K_j] and not keys[pygame.K_k]:
            self.twz = self.max_ang
        elif keys[pygame.K_k] and not keys[pygame.K_j]:
            self.twz = -self.max_ang

        if keys[pygame.K_SPACE]:
            self.tx = self.ty = self.tz = self.twz = 0.0

        if keys[pygame.K_ESCAPE]:
            raise KeyboardInterrupt

    def publish_cmd(self):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.twist.linear.x = self.vx
        msg.twist.linear.y = self.vy
        msg.twist.linear.z = self.vz
        msg.twist.angular.z = self.wz
        self.pub.publish(msg)

    def draw(self):
        self.screen.fill((20, 20, 20))

        lines = [
            "CLICK WINDOW FIRST",
            "MAV_FRAME = BODY_NED",
            f"target: x={self.tx:+.2f} y={self.ty:+.2f} z={self.tz:+.2f} yaw={self.twz:+.2f}",
            f"current: x={self.vx:+.2f} y={self.vy:+.2f} z={self.vz:+.2f} yaw={self.wz:+.2f}",
        ]

        y = 20
        for line in lines:
            text = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (20, y))
            y += 35

        pygame.display.flip()

    def control_loop(self):
        self.read_keyboard()

        self.vx = self.smooth_step(self.vx, self.tx)
        self.vy = self.smooth_step(self.vy, self.ty)
        self.vz = self.smooth_step(self.vz, self.tz)
        self.wz = self.smooth_step(self.wz, self.twz)

        self.publish_cmd()
        self.draw()
        self.clock.tick(60)

    def stop_and_cleanup(self):
        self.tx = self.ty = self.tz = self.twz = 0.0
        self.vx = self.vy = self.vz = self.wz = 0.0
        self.publish_cmd()
        pygame.quit()


def main():
    rclpy.init()
    node = RealtimeKeyboardDrone()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_and_cleanup()
        node.destroy_node()
        #rclpy.shutdown()


if __name__ == '__main__':
    main()
