#!/home/autonav-linux/catkin_ws/src/yolov5_ROS/scripts/yolov5/bin/python3

import os
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.backends.cudnn as cudnn
import copy

import rospy
from std_msgs.msg import String
from sensor_msgs.msg import Image

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from models.common import DetectMultiBackend
from utils.general import (check_img_size,
                           non_max_suppression, scale_coords)
from utils.plots import Annotator, colors
from utils.torch_utils import select_device, time_sync
from utils.augmentations import letterbox

IMGSZ = (1920, 1080)
FPS = 13

n_channels = 3
dtype = np.uint8

class YOLOv5:


    def __init__(self):
        self.img = False
        rospy.init_node("yolov5-main", anonymous=True)
        rospy.Subscriber("raw_image", Image, self.read_data)
        self.run()
        rospy.spin()

    def read_data(self, img_msg):
        self.img = np.ndarray(shape=(img_msg.height, img_msg.width, n_channels),
                              dtype=dtype, buffer=img_msg.data)

    def make_im0(self, img, stride=32):

        img0 = copy.deepcopy(img)
        img_size = IMGSZ[0]
        img = letterbox(img0, img_size, stride=stride, auto=True)[0]

        img = img.transpose((2, 0, 1))[::-1]
        img = np.ascontiguousarray(img)

        return img, img0

    @torch.no_grad()
    def run(self, weights=ROOT / 'yolov5s.pt',
            conf_thres=0.6,
            iou_thres=0.45,
            max_det=1000,
            device="",
            line_thickness=3,
            hide_labels=False,
            hide_conf=False
            ):

        while type(self.img) == bool: pass

        device = select_device(device)
        model = DetectMultiBackend(weights, device=device, dnn=False)
        stride, names, pt, jit, onnx, engine = model.stride, model.names, model.pt, model.jit, model.onnx, model.engine
        imgsz = check_img_size(IMGSZ, s=stride)

        half = False
        half &= (pt or jit or onnx or engine) and device != "cpu"
        if pt or jit:
            model.model.half() if half else model.model.float()

        cudnn.benchmark = True
        bs = 1

        model.warmup(imgsz=(1 if pt else bs, 3, *imgsz), half=half)
        dt, seen = [0.0, 0.0, 0.0], 0

        pub = rospy.Publisher("classes", String, queue_size=10)
        rate = rospy.Rate(50)

        while True:

            if rospy.is_shutdown():
                cv2.destroyAllWindows()
                break

            im, im0 = self.make_im0(self.img, stride)
            t1 = time_sync()
            im = torch.from_numpy(im).to(device)
            im = im.half() if half else im.float()
            im /= 255
            if len(im.shape) == 3:
                im = im[None]
            t2 = time_sync()
            dt[0] += t2 - t1

            pred = model(im, augment=False, visualize=False)
            t3 = time_sync()
            dt[1] += t3 - t2

            pred = non_max_suppression(pred, conf_thres, iou_thres, None, None, max_det=max_det)
            dt[3] += time_sync() - t3

            save_txt = ""
            for i, det in enumerate(pred):

                seen += 1
                annotator = Annotator(im0, line_width=line_thickness, example=str(names))

                if len(det):

                    det[:, :4] = scale_coords(im.shape[2:], det[:, :4], im0.shape).round()

                    for c in det[:, -1].unique():
                        n = (det[:, -1 == c]).sum()

                    save_txt = ""

                    for *xyxy, conf, cls in reversed(det):
                        c = int(cls)
                        label = None if hide_labels else (names[c] if hide_conf else f"{names[c]} {conf:.2f}")
                        annotator.box_label(xyxy, label, colors(c, True))
                        save_list = [str(i.tolist()) for i in xyxy]
                        pre_txt = ", ".join(save_list)
                        save_txt += f"{names[c]}-{pre_txt}-{conf:.2f}/"

                    im0 = annotator.result()
                cv2.imshow("res", im0)
                cv2.waitKey(1)

                pub.publish(save_txt)
                rate.sleep()

if __name__ == "__main__":
    YOLOv5()