from flask import render_template, redirect, Flask, request
from controller.controller import connect, get_interfaces_list,get_ip_route,get_arp,get_prefix_list

app = Flask(__name__)


@app.route('/')
def redirect_to_index():
    return redirect('/index', code=302)


@app.route('/index', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        result = request.form.to_dict()
        device = connect('cisco_ios', result['hostname'], result['username'], result['password'], result['port'],result['secret'])
        return render_template('index.html', result=get_interfaces_list(device), ip_route=get_ip_route(device),
                               arp=get_arp(device), prefix=get_prefix_list(device))
    else:
        return render_template('index.html')


@app.errorhandler(500)
def connection_time_out(e):
    return render_template('500.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5002,debug=True)
