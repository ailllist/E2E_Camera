#!/home/autonav-linux/catkin_ws/src/yolov5_ROS/scripts/yolov5/bin/python3

from std_msgs.msg import String
from sensor_msgs.msg import Image
from PIL import Image as img
import pyrealsense2 as rs
import numpy as np
import rospy
import cv2

FPS = 30
Width = 1280
Height = 720
Numpy_type_to_cvtype = {'uint8': '8U', 'int8': '8S', 'uint16': '16U',
                             'int16': '16S', 'int32': '32S', 'float32': '32F',
                             'float64': '64F'}

def cv2_to_imgmsg(img): # only activate at 3 channels camera
    img_msg = Image()
    img_msg.height = Height
    img_msg.width = Width
    cv_type = "%sC%d" % (Numpy_type_to_cvtype[str(img.dtype)], img.shape[2])
    img_msg.encoding = cv_type
    if img.dtype.byteorder == '>':
        img_msg.is_bigendian = True
    img_msg.data = img.tostring()
    img_msg.step = len(img_msg.data) // img_msg.height
    return img_msg

pipeline = rs.pipeline()
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

config.enable_stream(rs.stream.color, Width, Height, rs.format.bgr8, FPS)

# Start streaming
pipeline.start(config)
pub = rospy.Publisher("raw_image", Image, queue_size=10)
# pub = rospy.Publisher("raw_image", String, queue_size=10)
rospy.init_node("RealSense", anonymous=True)
rate = rospy.Rate(FPS)

while True:
    if rospy.is_shutdown():
        cv2.destroyWindow()
        break
    # Wait for a coherent pair of frames: depth and color
    frames = pipeline.wait_for_frames()
    color_frame = frames.get_color_frame()

    # Convert images to numpy arrays
    color_image = np.asanyarray(color_frame.get_data())

    color_image = np.asanyarray(color_frame.get_data())
    # print("%s" % list(color_image))
    # color_image = img.fromarray(color_image.astype(np.uint8))
    color_image = color_image.astype(np.uint8)
    pub.publish(cv2_to_imgmsg(color_image))
    rate.sleep()