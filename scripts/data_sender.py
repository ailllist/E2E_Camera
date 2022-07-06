import rospy
import numpy as np
from std_msgs.msg import String
from E2E_Camera import camera_data

Topic_list = rospy.get_published_topics()

class Data_sender:


    def __init__(self):
        self.send_txt = ""
        rospy.init_node("data_sender", anonymous=True)
        rospy.Subscriber("yolov5_classes", camera_data, self.read_data)
        self.send_data()
        rospy.spin()

    def read_data(self, data):
        # TODO data.__dir__() 확인.
        # self.send_txt += data.
        pass

    def send_data(self):
        pub = rospy.Publisher("classes", String, queue_size=10)
        rate = rospy.Rate(50)

        while True:

            pub.publish(self.send_txt)
            self.send_txt = ""
            rate.sleep()