import os
import cv2
import requests

from requests.auth import HTTPDigestAuth

pwd = "/home/iist"

class Camera:
    def __init__(self, _ip, _id, _pwd, _ip_3170="", _id_3170="", _pwd_3170="", model="1"):
        self.ip = _ip
        self.id = _id
        self.pwd = _pwd
        self.ip_3170 = _ip_3170
        self.id_3170 = _id_3170
        self.pwd_3170 = _pwd_3170
        self.model = model

        self.alarm_count = 0  # 반복 횟수
        self.alarm_status = 0  # detection 횟수
        self.error_count = 0
        self.alarm_object = ""

        self.alarm_on_str = f'http://{self.ip}/httpapi/WriteParam?action=writeparam&ETC_FLAMEDETECT_AlarmOutEnable=1'
        self.alarm_off_str = f'http://{self.ip}/httpapi/WriteParam?action=writeparam&ETC_FLAMEDETECT_AlarmOutEnable=0'
        self.rtsp = f'rtsp://{self.id}:{self.pwd}@{self.ip}/video1s1'
        self.cam = cv2.VideoCapture(self.rtsp)

        self.alarm_off_status = True

        self.auth = HTTPDigestAuth(self.id, self.id)
        self.default_set()

    def default_set(self):
        if self.model == "0":  # PTZ
            self.alarm_on_str = f'http://{self.ip_3170}/cgi-bin/admin/fwvamispecific.cgi?AlarmDisable=0&FwCgiVer=0x0001'
            self.alarm_off_str = f'http://{self.ip_3170}/cgi-bin/admin/fwvamispecific.cgi?AlarmDisable=1&FwCgiVer=0x0001'
            self.auth = HTTPDigestAuth(self.id_3170, self.pwd_3170)
        self.cam = cv2.VideoCapture(self.rtsp)
        self.alarm_off()

    def reconnect_cam(self):
        try:
            requests.get('http://' + self.ip, auth=self.auth, timeout=0.2)
            self.disconnect_cam()
            self.default_set()
            return True
        except:
            return False

    def disconnect_cam(self):
        self.cam.release()

    def read_frame(self):
        ret, self.frame = self.cam.read()
        if not ret:
            con_ = self.reconnect_cam()
            if not con_:
                self.error_count += 1
            if self.error_count == 10:
                f = open(os.path.join(pwd, "files/resource/log.txt"), 'a')
                f.write("reboot")
                f.close()
                os.system('echo "root1234" | sudo -kS /home/iist/detection.sh')
        return ret

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