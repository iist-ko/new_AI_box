import ultralytics

from ultralytics.engine.results import Results


class YOLOv8:
    def __init__(self, name, weight_path, conf_thr=.1, iou_thr=.05, persist=True, verbose=False,
                 tracker="./files/cfg/bytetrack.yaml"):
        self.name = name
        self.model = ultralytics.YOLO(weight_path)
        self.img_size = 640
        self.conf_thr = conf_thr
        self.iou_thr = iou_thr
        self.persist = persist
        self.verbose = verbose
        self.tracker = tracker

    def predict(self, frame) -> Results:
        # verbose = log output,
        return self.model.track(frame, persist=self.persist, conf=self.conf_thr, iou=self.iou_thr,
                                verbose=self.verbose, tracker=self.tracker)[0]

