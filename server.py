from flask import Flask, request
import MySQLdb
import json
from OpenSSL import SSL

app = Flask(__name__, static_folder='game')

conn = MySQLdb.connect(host="localhost", user="root", passwd="rootp", db="caves")
conn.autocommit(True)
cursor = conn.cursor()

def checkauth(req):
    print req
    if (not 'teamname' in req) or (not 'password' in req):
        return (False, 0, 0, 0)
    team_name = req['teamname']
    password = req['password']
    cursor.execute("select * from cred where Team = %s and password = %s", (team_name, password))
    if int(cursor.rowcount) > 0:
        result = cursor.fetchone()
  	return (True, int(result[2]), int(result[3]), int(result[4]))
    else:
	return (False, 0, 0, 0)

def levelnchallenge(n, data):
    try:
        print data
        if n < 8:
            req = json.loads(data)
            succ, level, d1, d2 = checkauth(req)
	    if succ is True and level >= n - 1:
		cursor.execute("select * from level" + str(n) + "ques where Team = %s", (req['teamname'],))
		response = {'challenge': cursor.fetchone()[1]}
	    elif succ is True:
		response = {'error': 'Solve previous chapters first'}
	    else:
		response = {'error': 'Invalid Credentials'}
	    return json.dumps(response)
        else:
	    response = {'error': 'Maximum level is 7'}
            return json.dumps(response)
    except Exception, e:
        print e
	response = {'error': 'There is some problem with the server'}
        return json.dumps(response)

def checkLeveln(n, data):
    try:
	if n < 8:
            req = json.loads(request.data)
	    succ, level, d1, d2 = checkauth(req)
	    if not 'answer' in req:
		response = {'error': 'Post data should contain an answer'}
		return json.dumps(response)
	    if succ is True:
		cursor.execute("select * from level" + str(n) + "sol where Team = %s and Password = %s", (req['teamname'], req['answer']))
		if int(cursor.rowcount) > 0:
		    if level == n - 1:
			cursor.execute("update cred set currentLevel = " + str(n) + " where Team = %s", (req['teamname'],))
		    response = {'success': True}
		else:
		    response = {'success': False}
	    else:
		response = {'error': 'Invalid Credentials'}
	    print response
	    return json.dumps(response);
        else:
	    response = {'error': 'Maximum level is 7'}
            return json.dumps(response)
    except:
	response = {'error': 'There is some problem with the server'}
        return json.dumps(response)

@app.route("/login", methods=['POST'])
def login():
    try:
        print request.data
        req = json.loads(request.data)
        succ, level, wf, sf = checkauth(req)
        if succ is True:
            response = {'ct': level, 'wf': bool(wf), 'sf': bool(sf)}
        else:
	    response = {'error': 'Invalid Credentials'}
        print response
        return json.dumps(response)
    except Exception, e:
        print e
	response = {'error': 'There is some problem with the server'}
        return json.dumps(response)


#@app.route("/level6challenge", methods=['POST'])
#def level6challenge():


@app.route("/challenge<int:n>", methods=['POST'])
def getchallenge(n):
    return levelnchallenge(n, request.data)

@app.route("/checkLevel<int:n>", methods=['POST'])
def checkLevel1(n):
    return checkLeveln(n, request.data)

@app.route("/fw", methods=['POST'])
def foundWand():
    try:
        req = json.loads(request.data)
        succ, level, d1, d2 = checkauth(req)
        if succ is True:
            if level == 3:
                cursor.execute("update cred set WandFound = 1 where Team = %s", (req['teamname'],))
                response = {'success': True}
            else:
                response = {'success': False}
        else:
            response = {'error': 'Invalid Credentials'}
        print response
        return json.dumps(response);
    except:
	response = {'error': 'There is some problem with the server'}
        return json.dumps(response)

@app.route("/fs", methods=['POST'])
def freeSpirit():
    try:
        req = json.loads(request.data)
        succ, level, d1, d2 = checkauth(req)
        if succ is True:
            if level == 3:
                cursor.execute("update cred set SpiritFreed = 1 where Team = %s", (req['teamname'],))
                response = {'success': True}
            else:
                response = {'success': False}
        else:
            response = {'error': 'Invalid Credentials'}
        print response
        return json.dumps(response);
    except:
	response = {'error': 'There is some problem with the server'}
        return json.dumps(response)

#context1 = ('server.crt', 'server.key')
#app.run(host='0.0.0.0', port=9999, threaded=True, ssl_context=context1)

app.run(host='0.0.0.0', port=9999, threaded=True)

