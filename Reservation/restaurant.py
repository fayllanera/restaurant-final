from flask import Flask, url_for, jsonify, request,  render_template, session, redirect
import sys, os, flask
import model
from flask_httpauth import HTTPBasicAuth
from flask_cors import cross_origin
from sqlalchemy import create_engine






app = Flask(__name__)
auth = HTTPBasicAuth()

def get_id(username):

    dbo = model.DBconn()

    cursor = dbo.getcursor()
    list = [username]
    cursor.callproc("getuser2", list)
    row = cursor.fetchall()
    return row



def spcall(qry, param, commit=False):
    try:
        dbo = model.DBconn()
        cursor = dbo.getcursor()
        cursor.callproc(qry, param)
        res = cursor.fetchall()
        if commit:
            dbo.dbcommit()
        return res
    except:
        res = [("Error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]),)]
    return res


@auth.get_password
def getpassword(username):
    return 'akolagini'


@app.route('/login/', methods=['POST'])
@cross_origin('*')
def login():
    auth = request.authorization

    # params = request.get_json()
    # password = params["password"]
    # email = params["email"]

    # res = spcall('login', (auth.username, auth.password), True)

    print(auth.username)
    return jsonify({'status': '200', 'roleid' : str(get_id(auth.username)), 'message': 'login successful!'})


@app.route('/reserve_accept/', methods=['POST'])
@cross_origin('*')
def schedule_accept():
    data = request.get_json()


    id = data['userid']
    if str(data['response']) == 'yes':
        status = "APPROVED"
        spcall('edit', (status, id), True)
        return jsonify({'message': 'Reserved!'})

    elif str(data['response']) == 'no':
        status = "DECLINED"
        spcall('edit', (status, id), True)
        return jsonify({'message': 'Reservation declined!'})


@app.route('/reservation/', methods=['POST'])
def reservation():

    params = request.get_json()
    diner = params["diner"]
    cus_name = params["cus_name"]
    cus_num = params["cus_num"]
    attendees = params["attendees"]
    res_date = params["res_date"]
    res_time = params["res_time"]

    res = spcall('reservations', (diner, cus_name, cus_num, attendees, res_date, res_time), True)
    if 'Error' in res[0][0]:
        return jsonify({'status': 'error', 'message': res[0][0]})

    return jsonify({'status': 'ok', 'message': res[0][0]})


@app.route('/reservations/', methods=['GET'])
def reservations():

    res = spcall('myreservation', (), True)

    if 'Error' in str(res[0][0]):
        return jsonify({'status': 'error', 'message': res[0][0]})

    recs = []
    for r in res:
        recs.append({"diner": str(r[0]), "cus_name": str(r[1]), "attendees": str(r[2]), "res_date": str(r[3]),
                     "res_time": str(r[4]), "cus_num": str(r[5]), "status": str(r[6]), "id": str(r[7])})
    return jsonify({'status': 'ok', 'entries': recs, 'count': len(recs)})


@app.route('/registration/', methods=['POST'])
def register():

    params = request.get_json()
    fname = params["fname"]
    cpnum = params["cpnum"]
    uname = params["uname"]
    pword = params["pword"]

    res = spcall('register', (fname, cpnum, uname, pword), True)
    if 'Error' in res[0][0]:
        return jsonify({'status': 'error', 'message': res[0][0]})

    return jsonify({'status': 'ok', 'message': res[0][0]})


@app.route('/search/', methods=['GET', 'POST', 'PUT'])
def search_res():

    params = request.get_json()
    resname1 = params["resname1"]

    res = spcall('res_search', (resname1, 'random'), True)
    if 'Error' in str(res[0][0]):
        return jsonify({'status': 'error', 'message': res[0][0]})

    recs = []

    for r in res:
        recs.append({"resname1": r[0], "address": r[1], "contact": r[2]})

    return jsonify({'status': 'ok', 'entries': recs, 'count': len(recs)})


@app.route('/rating', methods=['POST'])
def rate():
    params = request.get_json()
    answer = params["answer"]
    diner = params["diner"]
    print(answer)
    print(diner)
    res = spcall('rate', (str(answer), str(diner)), True)

    if 'Error' in res[0][0]:
        return jsonify({'status': 'error', 'message': res[0][0]})
    return jsonify({'status': 'ok', 'message': res[0][0]})


@app.route('/my_reservation', methods=['GET'])
def myreservation():
    res = spcall('myreservation', (), True)

    if 'Error' in str(res[0][0]):
       return jsonify({'status': 'error', 'message': res[0][0]})

    recs = []
    for r in res:
      recs.append({"diner": str(r[0]), "cus_name": str(r[1]), "attendees": str(r[2]), "res_date": str(r[3]), "res_time": str(r[4]), "cus_num": str(r[5]), "status": str(r[6])})
    return jsonify({'status': 'ok', 'entries': recs, 'count': len(recs)})


@app.route('/view_ratings', methods=['GET'])
def view_ratings():
    res = spcall('view_ratings', (), True)

    if 'Error' in str(res[0][0]):
       return jsonify({'status': 'error', 'message': res[0][0]})

    recs = []
    for r in res:
      recs.append({"diner_name": str(r[0]), "answer": str(r[1])})
    return jsonify({'status': 'ok', 'entries': recs, 'count': len(recs)})


@app.after_request
def add_cors(resp):
    resp.headers['Access-Control-Allow-Origin'] = flask.request.headers.get('Origin', '*')
    resp.headers['Access-Control-Allow-Credentials'] = True
    resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS, GET, PUT, DELETE'
    resp.headers['Access-Control-Allow-Headers'] = flask.request.headers.get('Access-Control-Request-Headers',
                                                                             'Authorization')
    # set low for debugging

    if app.debug:
        resp.headers["Access-Control-Max-Age"] = '1'
    return resp

if __name__=='__main__':
    app.run(debug=True)


# @app.route('/login', methods=['POST'])
# @auth.login_required
# def login():
#     params = request.get_json()
#
#     res = spcall('login', (params['username'], params['pass']))
#     print(str(res[0][0]))
#     if 'Error' in str(res[0][0]):
#         return jsonify(status='error', url='login.html')
#
#     return jsonify(status='success', url='restaurant.html')
#

# @app.route('/login', methods=['POST'])
# def login():
#     params = request.get_json()
#     pwd = params["pwd"]
#     username = params["username"]
#
#     res = spcall('login', (username, pwd), True)
#
#     if 'Error' in res[0][0]:
#         return jsonify({'status': 'error', 'message': res[0][0]})
#
#     return jsonify({'status': 'ok', 'message': res[0][0]})

# @app.route('/res_average', methods=['GET'])
# def res_average():
#     res = spcall('res_average', (), True)
#
#     if 'Error' in str(res[0][0]):
#         return jsonify({'status': 'error', 'message': res[0][0]})
#
#     recs = []
#     for r in res:
#      recs.append({"res_avg": str(r[0]), "diner_name": str(r[1])})
#     return jsonify({'status': 'ok', 'entries': recs, 'count': len(recs)})