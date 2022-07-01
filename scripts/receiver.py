#!/home/autonav-linux/catkin_ws/src/yolov5_ROS/scripts/yolov5/bin/python3

from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import rospy
import cv2

bridge = CvBridge()

def main(data):
    cv_image = bridge.imgmsg_to_cv2(data, "bgr8")
    cv2.imshow("raw_data", cv_image)

rospy.init_node("listener", anonymous=True)
rospy.Subscriber("raw_image", Image, main)
rospy.spin()