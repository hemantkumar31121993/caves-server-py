from flask import Flask, request
import MySQLdb
import json

app = Flask(__name__)

conn = MySQLdb.connect(host="localhost", user="root", passwd="wdinlm", db="caves")
cursor = conn.cursor()

def checkauth(req):
    print req
    if (not 'teamname' in req) or (not 'password' in req):
        return (False, 0)
    team_name = req['teamname']
    password = req['password']
    cursor.execute("select * from cred where Team = %s and password = %s", (team_name, password))
    if int(cursor.rowcount) > 0:
  	return (True, int(cursor.fetchone()[2]))
    else:
	return (False, 0)

def levelnchallenge(n, data):
    try:
        if n < 8:
            req = json.loads(data)
	    succ, level = checkauth(req)
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
    except:
	response = {'error': 'Exception occured'}
        return json.dumps(response)

def checkLeveln(n, data):
    try:
	if n < 8:
            req = json.loads(request.data)
	    succ, level = checkauth(req)
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
	response = {'error': 'Exception occured'}
        return json.dumps(response)
        
@app.route("/login", methods=['POST'])
def login():
    try:
        print request.data
        req = json.loads(request.data)
        succ, level = checkauth(req)
        if succ is True:
  	    response = {'completedTill': level}
        else:
	    response = {'error': 'Invalid Credentials'}
        return json.dumps(response)
    except:
	response = {'error': 'Exception occured'}
        return json.dumps(response)
        

@app.route("/level6challenge", methods=['POST'])
def level6challenge():
    

@app.route("/level<int:n>challenge", methods=['POST'])
def getchallenge(n):
    return levelnchallenge(n, request.data)

@app.route("/checkLevel<int:n>", methods=['POST'])
def checkLevel1(n):
    return checkLeveln(n, request.data)

app.run(host='0.0.0.0', port=9999, threaded=True)
 
