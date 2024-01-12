import os
import cv2
import json
import requests

from requests.auth import HTTPDigestAuth

from src import darknet

pwd = "/home/iist"
# pwd = os.getcwd()


def image_detection(image_path, network, class_names, class_colors, thresh):
    width = darknet.network_width(network)
    height = darknet.network_height(network)
    darknet_image = darknet.make_image(width, height, 3)

    image = image_path
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_size2 = cv2.resize(image, (width, height))
    image_resized = cv2.resize(image_rgb, (width, height),
                               interpolation=cv2.INTER_LINEAR)

    darknet.copy_image_from_bytes(darknet_image, image_resized.tobytes())
    detections = darknet.detect_image(network, class_names, darknet_image, thresh=thresh)
    darknet.free_image(darknet_image)
    image, point = darknet.draw_boxes(detections, image_resized, class_colors)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB), detections


def read_json(txt_file):
    f = json.loads(open(os.path.join(pwd, f"files/resource/{txt_file}"), 'r').read())
    read_data = f["data"]
    save_data = dict()
    key = 0
    for i in range(0, 32):
        try:
            data = read_data[str(i)]
            if data["ip"] and data["user_name"] and data["password"] and data["maker"]:
                save_data[str(key)] = data
                key += 1
        except KeyError:
            pass
    return save_data


def check_connect(ip_, id_, pwd_):
    try:
        requests.get(f"http://{ip_}/", auth=HTTPDigestAuth(id_, pwd_), timeout=0.5)
        return True
    except:
        return False


class Alarm:
    def __init__(self, ip_, id_, pwd_, model):
        self.ip = ip_
        self.id = id_
        self.pwd = pwd_
        self.alarm_count = 0  # 반복 횟수
        self.alarm_status = 0  # detection 횟수
        self.cam = None
        self.frame = None
        self.auth = None
        self.model = model
        self.alarm_off_status = True
        self.alarm_object = ""
        self.alarm_on_str = f'http://{self.ip}/httpapi/WriteParam?action=writeparam&ETC_FLAMEDETECT_AlarmOutEnable=1'
        self.alarm_off_str = f'http://{self.ip}/httpapi/WriteParam?action=writeparam&ETC_FLAMEDETECT_AlarmOutEnable=0'
        self.rtsp = f'rtsp://{self.id}:{self.pwd}@{self.ip}/video1s1'
        self.error_count = 0
        self.default_set()

    def default_set(self):
        print("[INFO] ====== Default_set ======")
        self.auth = HTTPDigestAuth(self.id, self.pwd)
        self.model_check()
        print("Alarm Off")
        self.cam = cv2.VideoCapture(self.rtsp)
        requests.get(self.alarm_off_str, auth=self.auth, timeout=0.5)

    def model_check(self):
        if self.model != "1":
            self.cam = self.rtsp = f"rtsp://{self.id}:{self.pwd}@{self.ip}/cam0_0"
            self.alarm_on_str = f'http://{self.ip}/cgi-bin/admin/fwvamispecific.cgi?AlarmDisable=0&FwCgiVer=0x0001'
            self.alarm_off_str = f'http://{self.ip}/cgi-bin/admin/fwvamispecific.cgi?AlarmDisable=1&FwCgiVer=0x0001'

    def reconnect_cam(self):
        try:
            requests.get('http://'+self.ip, auth=self.auth, timeout=0.2)
            self.disconnect_cam()
            self.default_set()
            return True
        except:
            return False

    def read_frame(self):
        ret, self.frame = self.cam.read()
        if not ret:
            print("frame read error")
            con_ = self.reconnect_cam()
            if not con_:
                self.error_count += 1
            if self.error_count == 10:
                f = open(os.path.join(pwd, "files/resource/log.txt"), 'a')
                f.write("reboot")
                f.close()
                os.system('echo "root1234" | sudo -kS /home/iist/detection.sh')
        return ret

    def disconnect_cam(self):
        self.cam.release()

    def alarm_off(self):
        if not self.alarm_off_status:
            print(self.ip + ' Alarm Off')
            status=requests.get(self.alarm_off_str, auth=self.auth, timeout=0.5)
            code = status.status_code
            self.alarm_off_status = True
            return code
        else:
            pass

    def alarm_on(self):
        if self.alarm_off_status:
            status = requests.get(self.alarm_off_str, auth=self.auth, timeout=0.5)
            code = status.status_code
            if code == 200:
                self.alarm_off_status = False
            else:
                self.alarm_off_status = True
            return code
        else:
            pass

    def reset(self):
        self.alarm_count = 0  # 반복 횟수
        self.alarm_status = 0  # detection 횟수
        self.alarm_object = ""


def connection_alarm(json_name):
    ip_data = read_json(json_name)
    alarm = []
    ip_data_len = len(ip_data)
    for i in range(ip_data_len):
        try:
            ip_, id_, pwd_, model_ = ip_data[str(i)].values()
        except KeyError as k:
            print(f"[{k}] : json 확인")
            continue
        except ValueError as v:
            print(f"[{v}] : json 확인")
            continue
        if check_connect(ip_, id_, pwd_):
            alarm.append(Alarm(ip_, id_, pwd_, model_))
        else:
            ip_data_len -= 1
            print(f"[CON Error] {ip_}")
    return alarm, ip_data_len