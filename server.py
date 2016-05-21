from flask import Flask, request
import MySQLdb
import json
import hashlib
from OpenSSL import SSL

app = Flask(__name__, static_folder='game')

conn = MySQLdb.connect(host="localhost", user="root", passwd="wdinlm", db="caves")
conn.autocommit(True)
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

def MD5(text):
    m = hashlib.md5()
    m.update(text)
    return m.hexdigest()

def levelnchallenge(n, data):
    try:
        print data
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

def getDESEncryption(teamname, plaintext):
    if plaintext == 'password':
        cursor.execute("select Challenge from level4 where Team = %s", (teamname,))
        return cursor.fetchone()[0]
    else:
	return "3bafebc456d7e789"
        
def getAESEncryption(teamname, plaintext):
    if plaintext == 'password':
        cursor.execute("select Challenge from level5 where Team = %s", (teamname,))
        return cursor.fetchone()[0]
    else:
	return "3bafebbcd6d7e789"

@app.route("/des", methods=['POST'])
def des():
    try:
        req = json.loads(request.data)
        if ('teamname' in req) and ('password' in req) and ('plaintext' in req):
	    if req['teamname'] in authenticDESTeams:
	        if authenticDESTeams[req['teamname']][0] == req['password']:
		    if MD5(req['plaintext']) == authenticDESTeams[req['teamname']][2]:
			cursor.execute("update cred set currentLevel = 4 where Team = %s", (req['teamname'],))
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

@app.route("/aes", methods=['POST'])
def aes():
    try:
        req = json.loads(request.data)
        print req;
        if ('teamname' in req) and ('password' in req) and ('plaintext' in req):
	    if req['teamname'] in authenticAESTeams:
	        if authenticAESTeams[req['teamname']][0] == req['password']:
		    if MD5(req['plaintext']) == authenticAESTeams[req['teamname']][3]:
			cursor.execute("update cred set currentLevel = 5 where Team = %s", (req['teamname'],))
                        response = {'success': True}
                    else:
	                encText = getAESEncryption(req['teamname'], req['plaintext']) 
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
	response = {'error': 'There is some problem with the server'}
        return json.dumps(response)

#context1 = ('server.crt', 'server.key')
#context1 = ('server.crt', 'server.key')
#app.run(host='0.0.0.0', port=9999, threaded=True, ssl_context=context1)

app.run(host='0.0.0.0', port=9999, threaded=True)

