import os
import cv2
import time
import psutil
import datetime
import threading

from src import darknet
from src.tools import read_json, Alarm, image_detection, check_connect

pwd = os.getcwd()


def main():

    # ---- ip setting end ---- #
    # ---- model load ---- #
    network, class_names, class_colors = \
        darknet.load_network(
            os.path.join(pwd, "files/cfg/yolov4-tiny-custom.cfg"),
            os.path.join(pwd, "files/data/obj.data"),
            os.path.join(pwd, "files/weights/yolov4-tiny-custom_8000.weights"),
            batch_size=1
        )
    # ---- model load end ---- #
    cap = cv2.VideoCapture(os.path.join(pwd, 'test_av/Video_2023-04-17_113227.wmv'))
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
        image, detections = image_detection(frame, network, class_names, class_colors, 0.4, 0.3)

        fire = 0
        smoke = 0

        for label, confidence, bbox in detections:
            if label == 'fire':
                fire += 1
                alarm_status += 1
            if label == 'Smoke':
                smoke += 1
                alarm_status += 1
            print(label)

            if fire > smoke:
                alarm_object = 'Fire'
            elif fire < smoke:
                alarm_object = 'Smoke'
            elif fire == smoke:
                alarm_object = 'Fire & Smoke'

        alarm_count += 1
        print(detections)
        cv2.putText(image, f"Detect: Object {alarm_object}", (250, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, [255, 255, 255], 2, cv2.LINE_AA)
        cv2.imshow('frame', image)
        if detections:
            time.sleep(0.5)
        if cv2.waitKey(20) == 27:
            break

    if cap.isOpened():
        cap.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
