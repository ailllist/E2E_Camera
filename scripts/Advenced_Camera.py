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

Traffic_list = ["R", "O", "G", "LR", "LG"]

class AdvCam:

    def __init__(self):
        self.recv_data = []
        self.containing_classes = {}
        rospy.init_node("Adv_Camera_exp", anonymous=True) # advanced_camera_experimental
        rospy.Subscriber("/yolov5/yolov5_classes", camera_data, self.read_data)
        self.send_data()
        rospy.spin()

    def class_holder(self, classes):
        TL_change = False
        all_classes = list(set([i[0] for i in classes]))
        prev_list = list(self.containing_classes.keys())
        for i in all_classes:
            if i in Traffic_list:
                TL_change = True

        for i in prev_list:
            if i in Traffic_list:
                if TL_change:
                    del self.containing_classes[i]
                    continue

            if i not in all_classes:
                self.containing_classes[i] += 1
                if self.containing_classes[i] >= CLASS_CNT:
                    del self.containing_classes[i]
            else:
                continue

        for i in all_classes:
            try:
                tmp_cnt = self.containing_classes[i]
                if tmp_cnt == 0: # detection이 잘 진행중인 경우
                    continue
                else: # detection이 끊어졌다가 다시 들어온 경우
                    self.containing_classes[i] = 0
            except: # 새로문 물체인 경우
                self.containing_classes[i] = 0


    def read_data(self, data):
        self.recv_data = seperator(data.yolov5)

    def send_data(self):
        pub = rospy.Publisher("Filtered_classes", String, queue_size=10)
        rate = rospy.Rate(10)
        while True:
            if rospy.is_shutdown():
                break
            # print("processing....")
            self.class_holder(self.recv_data)
            print(self.containing_classes)
            tmp_list = list(self.containing_classes.keys())
            txts = "/".join(tmp_list)
            print("txt: ", txts)
            pub.publish(txts)
            rate.sleep()


def seperator(classes_str: str) -> list:
    tmp_list = [i.split("-") for i in classes_str.split("/")]
    del tmp_list[len(tmp_list)-1]
    return tmp_list


if __name__ == "__main__":
    AdvCam()