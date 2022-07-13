#!/home/autonav-linux/catkin_ws/src/yolov5_ROS/scripts/yolov5/bin/python3

import rospy
from std_msgs.msg import String
from E2E_Camera.msg import camera_data

"""
This code is Dummy data
"""

class Adv_Cam:


    def __init__(self):
        self.recv_data = ""
        self.send_txt = ""
        rospy.init_node("Adv_Camera_exp", anonymous=True)
        rospy.Subscriber("/yolov5/yolov5-classes", camera_data, self.read_data)
        self.send_data()
        rospy.spin()

    def read_data(self, data):
        self.recv_data = data.yolov5

    def send_data(self):
        pub = rospy.Publisher("Filtered_classes", String, queue_size=10)
        rate = rospy.Rate(10)
        while True:
            pub.publish(self.send_txt)
            self.send_txt = ""
            rate.sleep()

if __name__ == "__main__":
    Adv_Cam()