import os
import cv2
import torch
import numpy as np

from utils.torch_yolo.torch_utils import select_device, non_max_suppression
from utils.torch_yolo.experimental import attempt_load

pwd = os.getcwd()


class YOLOv7:
    def __init__(self, weight, conf_thresh=.45, iou_thresh=.25, imgsz=640):
        self.conf_thresh = conf_thresh
        self.iou_thresh = iou_thresh
        device = "0" if torch.cuda.is_available() else "cpu"
        weight_path = os.path.join(pwd, weight)
        self.device = select_device(device=device)
        self.model = attempt_load(weights=weight_path, map_location="cuda")
        self.imgsz = imgsz
        self.model_init()

    def model_init(self):
        self.model.half()
        self.model(torch.zeros(1, 3, self.imgsz, self.imgsz)
                   .to(self.device)
                   .type_as(next(self.model.parameters())))
        self.model.eval()

    @torch.no_grad()
    def predict(self, img0):
        img = cv2.resize(img0, (640, 640))  # resize

        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB
        img = np.ascontiguousarray(img)

        img = torch.from_numpy(img).to(self.device)
        img = img.half()
        img /= 255.0

        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        pred = self.model(img, augment=False)[0]
        results = non_max_suppression(
            pred, conf_thres=self.conf_thresh, iou_thres=self.iou_thresh
        )
        if results:
            results = results[0]
        return results