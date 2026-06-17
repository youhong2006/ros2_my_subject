import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math

class TrajectoryPublisher(Node):

    def __init__(self):
        super().__init__('trajectory_publisher')
        
        # 建立發布者，話題為 /joint_states
        self.publisher_ = self.create_publisher(JointState, '/joint_states', 10)
        
        # 建立定時器，每 50 毫秒執行一次 [cite: 185]
        self.timer_ = self.create_timer(0.05, self.timer_callback)
        
        # 定義 5 個姿態點，這次要填入 6 個關節的數值 [cite: 191]
        # 關節順序對應：[arm_0_joint, arm_1_joint, arm_2_joint, arm_3_joint, gripper_1_joint, gripper_2_joint]
        self.points = [
            [0.0,   0.0,   0.0,   0.0,   0.0,  0.0],
            [1.57,  0.5,  -0.5,   0.5,   0.04, 0.04],
            [3.14,  1.0,  -1.0,   1.0,   0.0,  0.0],
            [-1.57, -0.5,  0.5,  -0.5,   0.05, 0.05],
            [0.0,  -1.0,   1.0,  -1.0,   0.02, 0.02]
        ]
        
        self.current_point_idx = 0
        self.next_point_idx = 1
        self.fraction = 0.0
        self.step = 0.02  # 控制移動的平滑度與速度

    def timer_callback(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        
        # 這裡必須跟你的 URDF 關節名稱完全一致
        msg.name = [
            'arm_0_joint', 
            'arm_1_joint', 
            'arm_2_joint', 
            'arm_3_joint', 
            'gripper_1_joint', 
            'gripper_2_joint'
        ]
        
        # 線性內插計算 [cite: 192]
        p1 = self.points[self.current_point_idx]
        p2 = self.points[self.next_point_idx]
        
        current_positions = []
        for i in range(len(p1)):
            val = p1[i] + self.fraction * (p2[i] - p1[i])
            current_positions.append(val)
            
        msg.position = current_positions
        self.publisher_.publish(msg)
        
        # 推進內插進度 [cite: 192]
        self.fraction += self.step
        if self.fraction >= 1.0:
            self.fraction = 0.0
            self.current_point_idx = self.next_point_idx
            self.next_point_idx = (self.next_point_idx + 1) % len(self.points) # 循環往復 [cite: 193]

def main(args=None):
    rclpy.init(args=args)
    node = TrajectoryPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()