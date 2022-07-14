#!/home/autonav-linux/catkin_ws/src/yolov5_ROS/scripts/yolov5/bin/python3

import rospy
from std_msgs.msg import String
from E2E_Camera.msg import camera_data

"""
이 코드는 카메라 필터에 대한 코드임. 
*** only for ERP-42 ***
"""

CLASS_CNT = 10 # default

try:
    param_list = list(rospy.get_param_names())
    for i in param_list:
        tmp_list = i.split("/")
        for j in tmp_list:
            if j == "class_cnt":
                CLASS_CNT = rospy.get_param(i)

except:
    pass

class AdvCam:

    def __init__(self):
        self.recv_data = []
        self.processed_txt = ""
        self.containing_classes = {}
        rospy.init_node("Adv_Camera_exp", anonymous=True) # advanced_camera_experimental
        rospy.Subscriber("/yolov5/yolov5-classes", camera_data, self.read_data)
        self.send_data()
        rospy.spin()

    def class_holder(self, classes):
        for i in classes:
            try:
                tmp_cnt = self.containing_classes[i[0]]
                if tmp_cnt < CLASS_CNT:
                    self.containing_classes[i[0]] += 1
                else:
                    del self.containing_classes[i[0]]

            except:
                self.containing_classes[i[0]] = 0

    def read_data(self, data):
        self.recv_data = seperator(data.yolov5)
        self.class_holder(self.recv_data)

    def send_data(self):
        pub = rospy.Publisher("Filtered_classes", String, queue_size=10)
        rate = rospy.Rate(10)
        while True:
            tmp_list = list(self.containing_classes.keys())
            self.processed_txt = "/".join(tmp_list)
            pub.publish(self.processed_txt)
            self.processed_txt = ""
            rate.sleep()


def seperator(classes_str: str) -> list:
    tmp_list = [i.split("-") for i in classes_str.split("/")]
    return tmp_list


if __name__ == "__main__":
    AdvCam()