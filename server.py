from flask import Flask, request, redirect, url_for, send_from_directory
import MySQLdb
import os
import json
import hashlib
from des import level4
from des import pyDES
from des import constants
from eaeae import level5
from OpenSSL import SSL
import traceback

app = Flask(__name__, static_folder='game')

conn = MySQLdb.connect(host="localhost", user="root", passwd="rootp", db="caves")
conn.autocommit(True)
conn.ping(True)
cursor = conn.cursor()

authenticDESTeams = dict();
cursor.execute("select a.Team, a.Password, b.DESKey, b.Password from cred a, level4 b where a.currentLevel > 2 and a.Team = b.Team");
data = cursor.fetchall();
for item in data:
    authenticDESTeams[item[0]] = (item[1], item[2], item[3]);
#print authenticDESTeams

authenticAESTeams = dict();
cursor.execute("select a.Team, a.Password, b.AMat, b.EVec, b.Password from cred a, level5 b where a.currentLevel > 3 and a.Team = b.Team");
data = cursor.fetchall();
for item in data:
    authenticAESTeams[item[0]] = (item[1], item[2], item[3], item[4]);
#print authenticAESTeams

def addAuthenticDESTeam(teamname, password):
    cursor.execute("select DESKey, Password from level4 where Team = %s", (teamname,))
    if int(cursor.rowcount) > 0:
        result = cursor.fetchone()
        authenticDESTeams[teamname] = (password, result[0], result[1])

def addAuthenticAESTeam(teamname, password):
    cursor.execute("select AMat, EVec, Password from level5 where Team = %s", (teamname,))
    if int(cursor.rowcount) > 0:
        result = cursor.fetchone()
        authenticAESTeams[teamname] = (password, result[0], result[1], result[2])

cursor.execute("Select Team, DESKey from level4")
result = cursor.fetchall()
for item in result:
    key_bin = pyDES.hex_to_binary(item[1])
    K0 = pyDES.shuffle(key_bin, constants.pc1)
    keys_components = [(K0[0:28], K0[28:56])]
    level4.keys[item[0]] = pyDES.generateKeys(keys_components)

#print level4.keys

cursor.execute("Select Team, AMat, EVec from level5")
result = cursor.fetchall()
#print result
for item in result:
    mat = []
    rows = item[1].split(";")
    count = 0
    for item1 in rows:
        mat.append([])
        values = item1.split(" ")
        for item2 in values:
            mat[count].append(int(item2))
        count += 1
    vec = []
    EVecValues = item[2].split(" ")
    for item1 in EVecValues:
        vec.append(int(item1))
    level5.keys[item[0]] = (mat, vec)

#print level5.keys

def checkauth(req):
    #print req
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

def MD5(text):
    m = hashlib.md5()
    m.update(text)
    return m.hexdigest()

def levelnchallenge(n, data):
    try:
        #print data
        if n < 8:
            req = json.loads(data)
            succ, level, d1, d2 = checkauth(req)
	    if succ is True and level >= n - 1:
		cursor.execute("select Challenge from level" + str(n) + " where Team = %s", (req['teamname'],))
		response = {'challenge': cursor.fetchone()[0]}
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
            if level < n - 1:
                response = {'error': 'Solve previous chapters first'}
                return json.dumps(response)
	    if not 'answer' in req:
		response = {'error': 'Post data should contain an answer'}
		return json.dumps(response)
	    if succ is True:
		cursor.execute("select * from level" + str(n) + " where Team = %s and Password = %s", (req['teamname'], req['answer']))
		if int(cursor.rowcount) > 0:
		    if level == n - 1:
                        if n == 3:
                            addAuthenticDESTeam(req['teamname'], req['password']);
			cursor.execute("update cred set currentLevel = " + str(n) + " where Team = %s", (req['teamname'],))
		    response = {'success': True}
		else:
		    response = {'success': False}
	    else:
		response = {'error': 'Invalid Credentials'}
	    #print response
	    return json.dumps(response);
        else:
	    response = {'error': 'Maximum level is 7'}
            return json.dumps(response)
    except:
	response = {'error': 'There is some problem with the server'}
        return json.dumps(response)

@app.errorhandler(404)
def pageNotFound(e):
    try:
        return redirect(url_for('static', filename='caves.html'))
    except Exception, e:
        print e

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'game'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/login", methods=['POST'])
def login():
    try:
        #print request.data
        req = json.loads(request.data)
        succ, level, wf, sf = checkauth(req)
        if succ is True:
            response = {'ct': level, 'wf': bool(wf), 'sf': bool(sf)}
        else:
	    response = {'error': 'Invalid Credentials'}
        #print response
        return json.dumps(response)
    except Exception, e:
        print e
	response = {'error': 'There is some problem with the server'}
        return json.dumps(response)


def level6challenge():
    try:
        req = json.loads(request.data)
        succ, level, d1, d2 = checkauth(req)
        if succ is True and level >= 5:
            cursor.execute("select n, Challenge from level6 where Team = %s", (req['teamname'],))
            temp = cursor.fetchone()
            challenge = "n=" + temp[0] + "\n\n" + req['teamname'] + ": This door has RSA encryption with exponent 5 and the password is " + temp[1]
            response = {'challenge': challenge}
        elif succ is True:
            response = {'error': 'Solve previous chapters first'}
        else:
            response = {'error': 'Invalid Credentials'}
        return json.dumps(response)
    except Exception, e:
        print e
	response = {'error': 'There is some problem with the server'}
        return json.dumps(response)

@app.route("/challenge<int:n>", methods=['POST'])
def getchallenge(n):
    if n == 6:
        return level6challenge()
    else:
        return levelnchallenge(n, request.data)

@app.route("/checkLevel<int:n>", methods=['POST'])
def checkLevel(n):
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
        #print response
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
        return json.dumps(response);
    except:
	response = {'error': 'There is some problem with the server'}
        return json.dumps(response)

def getDESEncryption(teamname, plaintext):
    if plaintext == 'password':
        cursor.execute("select Challenge from level4 where Team = %s", (teamname,))
        return cursor.fetchone()[0]
    else:
	return level4.desEncryption(plaintext, teamname)

def getEAEAEEncryption(teamname, plaintext):
    if plaintext == 'password':
        cursor.execute("select Challenge from level5 where Team = %s", (teamname,))
        return cursor.fetchone()[0]
    else:
	return level5.eaeaeEncryption(plaintext, teamname)

@app.route("/des", methods=['POST'])
def des():
    try:
        req = json.loads(request.data)
        if ('teamname' in req) and ('password' in req) and ('plaintext' in req):
	    if req['teamname'] in authenticDESTeams:
	        if authenticDESTeams[req['teamname']][0] == req['password']:
		    if MD5(req['plaintext']) == authenticDESTeams[req['teamname']][2]:
			cursor.execute("update cred set currentLevel = 4 where Team = %s and currentLevel = 3", (req['teamname'],))
                        addAuthenticAESTeam(req['teamname'], req['password'])
                        response = {'success': True}
                    else:
	                encText = getDESEncryption(req['teamname'], req['plaintext'])
                        response = {'ciphertext': encText, 'success': False}
	        else:
		    response = {'error': 'Invalid Credentials'}
	    else:
	        response = {'error': 'You are not allowed to play this level'}
        else:
	    response = {'error': 'POST parameters: teamname, password, plaintext'}
        return json.dumps(response)
    except Exception, e:
        print e
	response = {'error': 'There is some problem with the server'}
        return json.dumps(response)

@app.route("/eaeae", methods=['POST'])
def eaeae():
    try:
        req = json.loads(request.data)
        #print req;
        if ('teamname' in req) and ('password' in req) and ('plaintext' in req):
	    if req['teamname'] in authenticAESTeams:
	        if authenticAESTeams[req['teamname']][0] == req['password']:
		    if MD5(req['plaintext']) == authenticAESTeams[req['teamname']][3]:
			cursor.execute("update cred set currentLevel = 5 where Team = %s and currentLevel = 4", (req['teamname'],))
                        response = {'success': True}
                    else:
	                encText = getEAEAEEncryption(req['teamname'], req['plaintext'])
                        response = {'ciphertext': encText, 'success': False}
	        else:
		    response = {'error': 'Invalid Credentials'}
	    else:
	        response = {'error': 'You are not allowed to play this level'}
        else:
	    response = {'error': 'POST parameters: teamname, password, plaintext'}
        return json.dumps(response)
    except Exception, e:
        print e.message
        traceback.print_exc()
	response = {'error': 'There is some problem with the server'}
        return json.dumps(response)

#context1 = ('server.crt', 'server.key')
#context1 = ('server.crt', 'server.key')
#app.run(host='0.0.0.0', port=9999, threaded=True, ssl_context=context1)

app.run(host='0.0.0.0', port=9999, threaded=True)

