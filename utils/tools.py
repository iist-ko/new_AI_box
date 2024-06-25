import os
import cv2
import json
import requests

from requests.auth import HTTPDigestAuth

# from models import darknet

pwd = "/usr/src/ultralytics/new_AI_box"
# pwd = os.getcwd()


# def image_detection(image_path, network, class_names, class_colors, thresh):
#     width = darknet.network_width(network)
#     height = darknet.network_height(network)
#     darknet_image = darknet.make_image(width, height, 3)
#
#     image = image_path
#     image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     image_size2 = cv2.resize(image, (width, height))
#     image_resized = cv2.resize(image_rgb, (width, height),
#                                interpolation=cv2.INTER_LINEAR)
#
#     darknet.copy_image_from_bytes(darknet_image, image_resized.tobytes())
#     detections = darknet.detect_image(network, class_names, darknet_image, thresh=thresh)
#     darknet.free_image(darknet_image)
#     image, point = darknet.draw_boxes(detections, image_resized, class_colors)
#     return cv2.cvtColor(image, cv2.COLOR_BGR2RGB), detections


def read_json(txt_file):
    f = json.loads(open(os.path.join(pwd, f"files/resource/{txt_file}"), 'r').read())
    read_data = f["data"]
    save_data = dict()
    key = 0
    for i in range(0, 64):
        try:
            data = read_data[str(i)]
            if data["ip"] and data["id_"] and data["pw"] and data["maker"]:
                save_data[str(key)] = data
                key += 1
        except KeyError:
            continue
    return save_data


def check_connect(ip, id_, pw):
    try:
        requests.get(f"http://{ip}/", auth=HTTPDigestAuth(id_, pw), timeout=0.5)
        return True
    except:
        return False


class Alarm:
    def __init__(self, ip="", id_="", pw="", maker="", v_ip="", v_id="", v_pw=""):
        self.ip = ip
        self.id = id_
        self.pw = pw
        self.maker = maker
        self.auth = HTTPDigestAuth(id_, pw)

        self.v_ip = v_ip
        self.v_id = v_id
        self.v_pw = v_pw
        self.v_auth = HTTPDigestAuth(v_id, v_pw)

        self.alarm_count = 0  # 반복 횟수
        self.alarm_status = 0  # detection 횟수
        self.cam = None
        self.frame = None
        self.alarm_off_status = True
        self.alarm_object = ""
        self.alarm_on_str = f'http://{self.ip}/httpapi/WriteParam?action=writeparam&ETC_FLAMEDETECT_AlarmOutEnable=1'
        self.alarm_off_str = f'http://{self.ip}/httpapi/WriteParam?action=writeparam&ETC_FLAMEDETECT_AlarmOutEnable=0'
        self.rtsp = f'rtsp://{self.id}:{self.pw}@{self.ip}:554/video1s1'
        self.error_count = 0
        self.default_set()

    def default_set(self):
        print("[INFO] ====== Default_set ======")
        self.maker_check()
        print("Alarm Off")
        self.cam = cv2.VideoCapture(self.rtsp)
        requests.get(self.alarm_off_str, auth=self.auth, timeout=0.5)

    def maker_check(self):
        if self.maker == "0":
            self.rtsp = f'rtsp://{self.id}:{self.pw}@{self.ip}:554/video1s1'
            self.alarm_on_str = f'http://{self.v_ip}/cgi-bin/admin/fwvamispecific.cgi?AlarmDisable=0&FwCgiVer=0x0001'
            self.alarm_off_str = f'http://{self.v_ip}/cgi-bin/admin/fwvamispecific.cgi?AlarmDisable=1&FwCgiVer=0x0001'
        elif self.maker == "2":
            self.rtsp = f'rtsp://{self.id}:{self.pw}@{self.ip}:554/cam0_0'
            self.alarm_on_str = f'http://{self.ip}/cgi-bin/admin/fwvamispecific.cgi?AlarmDisable=0&FwCgiVer=0x0001'
            self.alarm_off_str = f'http://{self.ip}/cgi-bin/admin/fwvamispecific.cgi?AlarmDisable=1&FwCgiVer=0x0001'
        else:
            self.alarm_on_str = f'http://{self.ip}/httpapi/WriteParam?action=writeparam&ETC_FLAMEDETECT_AlarmOutEnable=1'
            self.alarm_off_str = f'http://{self.ip}/httpapi/WriteParam?action=writeparam&ETC_FLAMEDETECT_AlarmOutEnable=0'
            self.rtsp = f'rtsp://{self.id}:{self.pw}@{self.ip}:554/video1s1'

    def reconnect_cam(self):
        self.disconnect_cam()
        self.cam = cv2.VideoCapture(self.rtsp)

    def conn_check(self):
        try:
            response = requests.get('http://'+self.ip, auth=self.auth, timeout=0.2)
            if response.status_code == 200:
                return True
            else:
                self.disconnect_cam()
                self.default_set()
            return True
        except:
            return False

    def read_frame(self):
        ret, self.frame = self.cam.read()
        if not ret:
            print(f"frame read error {self.error_count}")
            con_ = self.conn_check()
            if con_:
                self.error_count += 1
            if self.error_count == 10:
                f = open(os.path.join(pwd, "files/resource/log.txt"), 'a')
                f.write(f"{self.ip} reconnect_cam")
                f.close()
                self.reconnect_cam()

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
            data = ip_data[str(i)]
        except KeyError as k:
            print(f"[{k}] : json 확인")
            continue
        except ValueError as v:
            print(f"[{v}] : json 확인")
            continue

        if check_connect(data["ip"], data["id_"], data["pw"]):
            alarm.append(Alarm(**data))
        else:
            ip_data_len -= 1
            print(f"[CON Error] {data['ip']}")
    return alarm, ip_data_len


class DataStruct:
    def __init__(self, ip="", id_="", pw="", maker="", v_ip="", v_id="", v_pw=""):
        """
        :param ip: ptz ip address
        :param id_: ptz id
        :param pw: ptz password
        :param maker: str() ptz:0, fix-t:1, fix-s:2
        :param v_ip: video server ip address
        :param v_id: video server id
        :param v_pw: video server password
        """
        self.ip = ip
        self.id = id_
        self.pw = pw
        self.maker = maker
        self.v_ip = v_ip
        self.v_id = v_id
        self.v_pw = v_pw

def check_file(path):
    if not os.path.exists(path):
        os.makedirs(path)

def log_writer(path, txt):
    check_file(path)

    with open(path, 'a') as f:
        f.write(txt + "\n")
        f.close()