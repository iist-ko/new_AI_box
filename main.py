import os
import time
import psutil
import datetime

from models import darknet
# from models import YOLOv8
from utils.tools import image_detection, connection_alarm, log_writer

pwd = "/home/iist"


def main():
    index = 0

    # ---- ip setting ---- #
    json_name = 'rtsp.json'
    alarm, ip_data_len = connection_alarm(json_name)
    # ---- ip setting end ---- #

    # ---- model load ---- #
    configure = {"name": "AI-Box",
                 "weight_path": os.path.join(pwd, 'files/weights/yolov8n.engine'),
                 "config_thr": .6,
                 "iou_thr": .5,
                 "persist": True,
                 "verbose": True
                 }

    # model = YOLOv8(**configure)

    network, class_names, class_colors = \
        darknet.load_network(
            os.path.join(pwd, "files/cfg/yolov4-tiny-custom.cfg"),
            os.path.join(pwd, "files/data/obj.data"),
            os.path.join(pwd, "files/weights/yolov4-tiny-custom_8000.weights"),
            batch_size=1
        )
    # ---- model load end ---- #

    try:
        point = alarm[index]
    except IndexError as e:
        print("[Not Connect cam]")

    epoch = 0

    while point:
        prev_time = time.time()
        if point.alarm_count == 0:
            print(f"[INFO] : Searching {point.ip} . . .")
        ret = point.read_frame()
        if not ret:
            point.reset()
            index += 1
            if index >= ip_data_len:  # ip 길이랑 같을때 초기화
                index = 0
            point = alarm[index]
        try:
            image, detections = image_detection(point.frame, network, class_names, class_colors, 0.50)

            fire = 0
            smoke = 0

            for label, confidence, bbox in detections:
                if label == 'fire':
                    fire += 1
                    point.alarm_status += 1
                if label == 'Smoke':
                    smoke += 1
                    point.alarm_status += 1

            if fire > smoke:
                point.alarm_object = 'Fire'
            elif fire < smoke:
                point.alarm_object = 'Smoke'
            elif fire == smoke:
                point.alarm_object = 'Fire & Smoke'

            point.alarm_count += 1

            if point.alarm_count == 10:
                if point.alarm_status >= 2:
                    print(f"[Detect] {point.ip} ")
                    status = point.alarm_on()
                    if status == 404:
                        continue
                    now = datetime.datetime.now()
                    nowDatetime = now.strftime('  %m-%d %H:%M:%S  ')

                    data = ""
                    data += point.ip
                    data += nowDatetime
                    data += point.alarm_object
                    log_writer(os.path.join(pwd, 'files/resource/log.txt'), data)
                else:
                    point.alarm_off()
                point.reset()
                index += 1
                if index >= ip_data_len:  # ip 길이랑 같을때 초기화
                    index = 0
                    epoch += 1
                    if epoch == 10:
                        alarm, ip_data_len = connection_alarm(json_name)
                        epoch = 0
                point = alarm[index]      # 다음 ip로 이동
            fps = int(1/(time.time() - prev_time))
            print(f"[INFO] 1 Frame FPS = {fps}")

            memory_usage_dict = dict(psutil.virtual_memory()._asdict())
            memory_usage_percent = memory_usage_dict['percent']
            if int(memory_usage_percent) >= 92:
                print("pkill!!")
                os.system('echo "root1234" | sudo -kS sh /home/iist/detection.sh')
        except:
            point.reset()
            index += 1
            if index >= ip_data_len:  # ip 길이랑 같을때 초기화
                index = 0
                epoch += 1
                if epoch == 10:
                    alarm, ip_data_len = connection_alarm(json_name)
                    epoch = 0
            point.disconnect_cam()
            point = alarm[index]
        time.sleep(0.2)


if __name__ == "__main__":
    main()
