from flask import render_template, redirect, Flask, request, url_for

import json
from controller.controller import *
from controller.controller import get_arp, get_interfaces_list, get_ip_route, get_prefix_list, connect, get_hostname, \
    get_vlans

app = Flask(__name__)


@app.route('/')
def redirect_to_index():
    return redirect('/index', code=302)


@app.route('/index', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        result = request.form.to_dict()
        device = connect('cisco_ios', result['hostname'], result['username'], result['password'], result['port'],
                         result['secret'])
        return render_template('index.html', result=get_interfaces_list(device), ip_route=get_ip_route(device),
                               arp=get_arp(device), prefix=get_prefix_list(device), hostname=get_hostname(device),
                               vlan=get_vlans(device))
    else:
        return render_template('first_page.html')


@app.route('/config', methods=['POST', 'GET'])
def config():
    if request.method == 'POST':
        result = request.form.to_dict()
        device = connect('cisco_ios', result['hostname'], result['username'], result['password'], result['port'],
                         result['secret'])

        with open("device.json", "w") as outfile:
            json.dump(result, outfile)

        return render_template('switch.html', vlan=get_vlans(device))
    else:
        with open('device.json', 'r') as openfile:
            x = json.load(openfile)
        device = connect('cisco_ios', x['hostname'], x['username'], x['password'], x['port'],
                         x['secret'])
        return render_template('switch.html', vlan=get_vlans(device))


@app.route('/config2', methods=['POST', 'GET'])
def config2():
    with open('device.json', 'r') as openfile:
        x = json.load(openfile)
    device = connect('cisco_ios', x['hostname'], x['username'], x['password'], x['port'],
                     x['secret'])

    id = request.form.get('id')
    name = request.form["name"]
    interface = request.form["interface"]
    mode = request.form["mode"]
    vlan = request.form["vlan"]
    # command = "conf t" + "\n" + "vlan " + id + "\n" + "name " + name + "\n" + "interface " + interface + "\n" + "switchport mode " + mode + "\n" + "switchport acces vlan " + vlan + "\n" + "end"
    device.enable()
    # print(command)

    print(device.send_command_timing("conf t"))
    print(device.send_command_timing("vlan "+id))
    print(device.send_command_timing("name "+name))
    print(device.send_command_timing("switchport mode "+mode))
    print(device.send_command_timing("switchport access "+vlan))
    print(device.send_command_timing("interface "+interface))

    return redirect(url_for('config'))


@app.route('/config3', methods=['POST', 'GET'])
def config3():
    with open('device.json', 'r') as openfile:
        x = json.load(openfile)
    device = connect('cisco_ios', x['hostname'], x['username'], x['password'], x['port'],
                     x['secret'])

    del_id = request.form.get('del_id')
    command_del = "conf t" + "\n" + "no vlan " + del_id
    device.enable()
    print(device.send_command_timing(command_del))

    return redirect(url_for('config'))


@app.errorhandler(500)
def connection_time_out(e):
    return render_template('500.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
