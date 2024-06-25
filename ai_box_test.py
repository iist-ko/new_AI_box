import os
import cv2
import time

from models import YOLOv8
# from utils.tools import image_detection

pwd = os.getcwd()


def main():
    configure = {"name": "AI-Box",
                 "weight_path": os.path.join(pwd, 'files/weights/v8n.engine'),
                 "conf_thr": .6,
                 "iou_thr": .5,
                 "persist": True,
                 "verbose": False
                 }
    # ---- ip setting end ---- #
    # ---- model load ---- #
    fire_label = 1
    smoke_label = 2
    model = YOLOv8(**configure)

    # ---- model load end ---- #
    cap = cv2.VideoCapture("rtsp://root:root@192.168.0.250:554/cam0_1")
    alarm_status = 0
    alarm_count = 0
    alarm_object = 0

    fps_ = int(cap.get(cv2.CAP_PROP_FPS))
    print(fps_)
    time.sleep(5)

    while True:
        prev_time = time.time()
        ret, frame = cap.read()
        if alarm_count == 0:
            print(f"[INFO] : Searching . . .")
        if not ret:
            print("video error")
            break
        detections = model.predict(frame)
        label = detections.boxes.cls.cpu().numpy()
        fire = 0
        smoke = 0

        if fire_label in label:
            fire_label += 1
        if smoke_label in label:
            smoke_label += 1

        print(label)

        alarm_count += 1
        if cv2.waitKey(30) == 27:
            break

    if cap.isOpened():
        cap.release()


if __name__ == "__main__":
    main()
