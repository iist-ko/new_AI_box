from flask import Flask, render_template, request
import os
import json

from src.tools import read_json

app = Flask(__name__)

# pwd = "/home/iist"
pwd = os.getcwd()

@app.route('/', methods=['GET'])
def hellohtml():
    if request.method == 'GET':
        ###################파일불러오기함수####################
        t = 0
        Rdata = read_json('rtsp.json')
        # print(Rdata)
        mylist = [['', '', '', ''] for i in range(16)]
        while t < len(Rdata):
            try:
                Data = Rdata[str(t)]
                mylist[t] = [Data["ip"], Data["user_name"], Data["password"], Data["maker"]]
            except KeyError:
                break
            t += 1
        return render_template("form.html", mylist=mylist)


@app.route('/method', methods=['GET', 'POST'])
def method():

    if request.method == 'GET':
        # args_dict = request.args.to_dict()
        # print(args_dict)
        num = request.args["num"]
        name = request.args.get("name")
        return "GET으로 전달된 데이터({}, {})".format(num, name)

    else:
        form_dict = request.form.to_dict()
        file_path = os.path.join(pwd, "files/resource/rtsp.json")
        with open(file_path, "r", encoding="utf-8") as json_file:
            json_data = json.loads(json_file.read())
            json_file.close()
        data = json_data["data"]
        index = 0
        for i in range(16):
            if form_dict[f"ip_{i}"] == '' or form_dict[f"id_{i}"] == '' or form_dict[f"pwd_{i}"] == '':
                if i < len(data):
                    del data[str(i)]
                pass
            if i < len(data):
                data_i = dict()
                data_i["ip"] = form_dict[f"ip_{i}"]
                data_i["user_name"] = form_dict[f"id_{i}"]
                data_i["password"] = form_dict[f"pwd_{i}"]
                data_i["maker"] = form_dict[f"mk_{i}"]
                data[str(index)] = data_i
                index += 1
            else:
                data[str(index)] = {"ip": form_dict[f"ip_{i}"], "user_name": form_dict[f"id_{i}"],
                                "password": form_dict[f"pwd_{i}"], "maker": form_dict[f"mk_{i}"]}
                index += 1

        json_data["data"] = data
        with open(os.path.join(pwd, "files/resource/rtsp.json"), 'w', encoding="utf-8") as f:
            json.dump(json_data, f, indent=4)
            f.close()


        return render_template("Success.html")


@app.route('/method2', methods=['GET', 'POST'])
def method2():
    os.system('echo "root1234" | sudo -kS reboot')
    return 'Reboot'


@app.route('/method3', methods=['GET', 'POST'])
def method3():
    f = open(os.path.join(pwd, "files/resource/log.txt"), 'r')
    strings = f.read()
    f.close()
    return render_template("Log.html", log_status=strings)


@app.route('/method4', methods=['GET', 'POST'])
def method4():
    ###################파일불러오기함수####################
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
        return "GET으로 전달된 데이터({}, {})".format(num, name)

    else:
        Add = request.form["Add"]
        Net = request.form["Net"]
        Gat = request.form["Gat"]
        Bro = request.form["Bro"]
        with open(os.path.join(pwd, "files/resource/IpChange.txt"), "w", encoding='utf-8') as f:
            f.write("%s\n%s\n%s\n%s" % (Add, Net, Gat, Bro))
            f.close()
        with open("/etc/network/interfaces", "w", encoding='utf-8') as f2:
            f2.write(
                "auto eth0\niface eth0 inet static\naddress  %s\nnetmask 255.255.255.0\nnetwork %s\ngateway %s\nbroadcast %s\ndns-nameservers %s 8.8.8.8" % (
                Add, Net, Gat, Bro, Add))
            f2.close()
        return render_template("Success.html")


@app.route('/method6', methods=['GET', 'POST'])
def method6():
    os.system('echo "root1234" | sudo -kS /home/iist/detection.sh')
    return "재 실"


if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')
