#!/home/autonav-linux/catkin_ws/src/yolov5_ROS/scripts/yolov5/bin/python3

from std_msgs.msg import String
from sensor_msgs.msg import Image
import rospy
import numpy as np
import cv2
import time

n_channels = 3
dtype = np.uint8

def imgmsg_to_cv2(img_msg):
    im = np.ndarray(shape=(img_msg.height, img_msg.width, n_channels),
                    dtype=dtype, buffer=img_msg.data)
    return im

def main(data):
    s_time = time.time()
    cv_image = imgmsg_to_cv2(data)
    cv2.imshow("raw_data", cv_image)
    cv2.waitKey(1)
    print(cv_image)
    print(time.time() - s_time)

rospy.init_node("listener", anonymous=True)
rospy.Subscriber("raw_image", Image, main)
rospy.spin()