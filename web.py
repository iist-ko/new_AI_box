from flask import Flask, render_template, request
import os
import json

from utils.tools import read_json
from utils.tools import DataStruct

app = Flask(__name__)

# pwd = "/home/iist"
pwd = "/usr/src/ultralytics/new_AI_box"
# pwd = os.getcwd()

@app.route('/', methods=['GET'])
def hellohtml():
    if request.method == 'GET':
        t = 0
        Rdata = read_json('rtsp.json')
        print(Rdata)
        mylist = [DataStruct() for _ in range(64)]
        while t < len(Rdata):
            try:
                Data = Rdata[str(t)]
                mylist[t] = DataStruct(**Data)
            except KeyError:
                print("Ee")
                break
            t += 1
        print(mylist[0].ip)
        return render_template("form.html", mylist=mylist)


@app.route('/method', methods=['GET', 'POST'])
def method():

    if request.method == 'GET':
        # args_dict = request.args.to_dict()
        # print(args_dict)
        num = request.args["num"]
        name = request.args.get("name")
        return "GET send data({}, {})".format(num, name)

    else:
        form_dict = request.form.to_dict()
        file_path = os.path.join(pwd, "files/resource/rtsp.json")

        with open(file_path, "r", encoding="utf-8") as json_file:
            json_data = json.loads(json_file.read())
            json_file.close()

        data = json_data["data"]
        data_len = len(data)
        index = 0
        for i in range(64):
            if form_dict[f"ip_{i}"] == '' or form_dict[f"pw_{i}"] == '':
                if i < data_len:
                    del data[str(i)]
                continue

            if i < data_len:
                if form_dict[f"ip_{i}"] != "" and form_dict[f"id_{i}"] != "" and form_dict[f"pw_{i}"] != "":
                    data_i = dict()
                    data_i["ip"] = form_dict[f"ip_{i}"]
                    data_i["id_"] = form_dict[f"id_{i}"]
                    data_i["pw"] = form_dict[f"pw_{i}"]
                    data_i["maker"] = form_dict[f"mk_{i}"]
                    data_i["v_ip"] = form_dict[f"server_ip_{i}"]
                    data_i["v_id"] = form_dict[f"server_id_{i}"]
                    data_i["v_pw"] = form_dict[f"server_pw_{i}"]
                    data[str(index)] = data_i
                    index += 1
            else:
                data[str(index)] = {"ip": form_dict[f"ip_{i}"], "id_": form_dict[f"id_{i}"],
                                    "pw": form_dict[f"pw_{i}"], "v_ip": form_dict[f"server_ip_{i}"],
                                    "v_id": form_dict[f"server_id_{i}"],
                                    "v_pw": form_dict[f"server_pw_{i}"], "maker": form_dict[f"mk_{i}"]}
                index += 1

        json_data["data"] = data
        with open(os.path.join(pwd, "files/resource/rtsp.json"), 'w', encoding="utf-8") as f:
            json.dump(json_data, f, indent=4)
            f.close()

        return render_template("Success.html")


@app.route('/method2', methods=['GET', 'POST'])
def method2():
    os.system('echo "echo \'root1234\' | sudo -kS reboot" > /hostpipe')
    return 'Reboot'


@app.route('/method3', methods=['GET', 'POST'])
def method3():
    f = open(os.path.join(pwd, "files/resource/log.txt"), 'r')
    strings = f.read()
    f.close()
    return render_template("Log.html", log_status=strings)


@app.route('/method4', methods=['GET', 'POST'])
def method4():
    t = 0
    f2 = open(os.path.join(pwd, "files/resource/IpChange.txt"), 'r')

    R2data = f2.read().split('\n')
    # print(Rdata)
    CH = ['', '', '', '']
    CH[0] = R2data[0]
    CH[1] = R2data[1]
    CH[2] = R2data[2]
    CH[3] = R2data[3]
    return render_template("IpChange.html", Ch0=CH[0], Ch1=CH[1], Ch2=CH[2], Ch3=CH[3])


@app.route('/method5', methods=['GET', 'POST'])
def method5():
    if request.method == 'GET':
        # args_dict = request.args.to_dict()
        # print(args_dict)
        num = request.args["Add"]
        name = request.args.get("Net")
        return "GET send data({}, {})".format(num, name)

    else:
        Add = request.form["Add"]
        Net = request.form["Net"]
        Gat = request.form["Gat"]
        Bro = request.form["Bro"]
        txt = f"auto eth0\niface eth0 inet static\naddress  {Add}\nnetmask {Net}\ngateway {Gat}\nbroadcast {Bro}\ndns-nameservers {Add} 8.8.8.8"
        with open(os.path.join(pwd, "files/resource/IpChange.txt"), "w", encoding='utf-8') as f:
            f.write("%s\n%s\n%s\n%s" % (Add, Net, Gat, Bro))
            f.close()
        with open("/interfaces", "w", encoding='utf-8') as f2:
            f2.write(txt)
            f2.close()
        return render_template("Success.html")


@app.route('/method6', methods=['GET', 'POST'])
def method6():
    os.system(f'{pwd}/detection.sh')
    return "restart"


if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')
