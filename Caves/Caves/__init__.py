from flask import Flask, request, redirect, url_for, send_from_directory
import dbsettings as db
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
import logging
import time

#logging.basicConfig(level=logging.DEBUG, filename='caves.log')
#log = logging.getLogger('werkzeug')
# prevent logging unnecessary info
#log.setLevel(logging.INFO)

staticFolder = 'static'
app = Flask(__name__, static_folder=staticFolder)

# takes input a string and returns another string with the non ASCII characters stripped
def stripNonASCII(string):
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)

conn = MySQLdb.connect(host=db.host, user=db.user, passwd=db.password, db=db.database)
conn.autocommit(True)
# ping the mysql server at regular interval so that the connection doesn't times
# out due to inactivity
conn.ping(True)
cursor = conn.cursor()

# caches information about the teams which are allowed to play the DES level
# so that we don't have to query database every time they send an
# encryption request
authenticDESTeams = dict();
cursor.execute("select a.Team, a.Password, b.Password from cred a, level4 b where a.currentLevel > 2 and a.SpiritFreed = 1 and a.Team = b.Team");
data = cursor.fetchall();
for item in data:
    authenticDESTeams[item[0]] = (item[1], item[2]);

# caches information about the teams which are allowed to play the EAEAE level
# so that we don't have to query database every time they send an
# encryption request
authenticEAEAETeams = dict();
cursor.execute("select a.Team, a.Password, b.Password from cred a, level5 b where a.currentLevel > 3 and a.Team = b.Team");
data = cursor.fetchall();
for item in data:
    authenticEAEAETeams[item[0]] = (item[1], item[2]);

# function to add a team info to authenticDESTeams: will be called when a team
# clears level 3 and moves to level 4
def addAuthenticDESTeam(teamname, password):
    if teamname not in authenticDESTeams:
        cursor.execute("select Password from level4 where Team = %s", (teamname,))
        if int(cursor.rowcount) > 0:
            result = cursor.fetchone()
            authenticDESTeams[teamname] = (password, result[0])

# function to add a team info to authenticEAEAETeams: will be called when a team
# clears level 4 and moves to level 5
def addAuthenticEAEAETeam(teamname, password):
    if teamname not in authenticEAEAETeams:
        cursor.execute("select Password from level5 where Team = %s", (teamname,))
        if int(cursor.rowcount) > 0:
            result = cursor.fetchone()
            authenticEAEAETeams[teamname] = (password, result[0])

# cache the DES keys in the dictionary level4.keys, so that we don't need to
# query database again and again
cursor.execute("Select Team, DESKey from level4")
result = cursor.fetchall()
for item in result:
    key_bin = pyDES.hex_to_binary(item[1])
    K0 = pyDES.shuffle(key_bin, constants.pc1)
    keys_components = [(K0[0:28], K0[28:56])]
    level4.keys[item[0]] = pyDES.generateKeys(keys_components)

# cache the EAEAE keys in the dictionary level5.keys, so that we don't need to
# query database again and again
cursor.execute("Select Team, AMat, EVec from level5")
result = cursor.fetchall()
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

# function to check authentication of a team.
# inp: req body in json
# out: Tuple (Is Auth Success, Current Level of Team, Wand Found or Not, Spirit Freed or Not)
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

# returns md5 digest
# inp: string to hash
# out: digest in hex
def MD5(text):
    m = hashlib.md5()
    m.update(text)
    return m.hexdigest()

# fetch challenge for levels 1 to 5 and level 7. Function for level 6 is seperate
# inp: level number, query data (in json string)
# out: json response string directly to send to the client
# parses input json to dict, validates it and returns appropriate response
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
    except: # Exception, e:
        logging.error(traceback.format_exc())
        #print e
	response = {'error': 'There is some problem with the server'}
        return json.dumps(response)

# fetch challenge for level 6
# out: json response string directly to send to the client
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
    except: # Exception, e:
        logging.error(traceback.format_exc())
        #print e
	response = {'error': 'There is some problem with the server'}
        return json.dumps(response)

# checks the solution a client sends for levels 1,2,3,6,7.
# checking solution for level 4 is done on /des endpoint
# checking solution for level 5 is done on /eaeae endpoint
# inp: level number, query data (in json string)
# out: json response string directly to send to the client
# parses input json to dict, validates it and returns appropriate response
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
			cursor.execute("update cred set currentLevel = " + str(n) + " where Team = %s", (req['teamname'],))
                        cursor.execute("update level" + str(n) + " set CompletedAt = %s where Team = %s", (time.strftime('%Y-%m-%d %H:%M:%S'), req['teamname']))
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
    except Exception, e:
        print e
        logging.error(traceback.format_exc())
	response = {'error': 'There is some problem with the server'}
        return json.dumps(response)

# navigate to our game url every time 404 error occurs
@app.errorhandler(404)
def pageNotFound(e):
    try:
        return redirect(url_for('static', filename='caves.html'))
    except: # Exception, e:
        logging.error(traceback.format_exc())
        #print e

# route for browser icon
@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, staticFolder), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# route for login
# post parameters: teamname, password
# post format: json
@app.route("/login", methods=['POST'])
def login():
    try:
        #print request.data
        req = json.loads(stripNonASCII(request.data))
        succ, level, wf, sf = checkauth(req)
        if succ is True:
            response = {'ct': level, 'wf': bool(wf), 'sf': bool(sf)}
        else:
	    response = {'error': 'Invalid Credentials'}
        #print response
        return json.dumps(response)
    except: # Exception, e:
        #print e
        logging.error(traceback.format_exc())
	response = {'error': 'There is some problem with the server'}
        return json.dumps(response)

# route for getting challenge for level 1 - 7
# post parameters: teamname, password
# post format: json
@app.route("/challenge<int:n>", methods=['POST'])
def getchallenge(n):
    if n == 6:
        return level6challenge()
    else:
        return levelnchallenge(n, stripNonASCII(request.data))

# route for checking solution of level 1 - 7
# post parameters: teamname, password, answer
# post format: json
@app.route("/checkLevel<int:n>", methods=['POST'])
def checkLevel(n):
    return checkLeveln(n, stripNonASCII(request.data))

# route for marking that a team has found the magical wand
# post parameters: teamname, password
# post format: json
@app.route("/fw", methods=['POST'])
def foundWand():
    try:
        req = json.loads(stripNonASCII(request.data))
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
        logging.error(traceback.format_exc())
	response = {'error': 'There is some problem with the server'}
        return json.dumps(response)

# route for marking that a team has freed the spirit
# post parameters: teamname, password
# post format: json
@app.route("/fs", methods=['POST'])
def freeSpirit():
    try:
        req = json.loads(stripNonASCII(request.data))
        succ, level, d1, d2 = checkauth(req)
        if succ is True:
            if level == 3 and d1 == 1:
                if req['teamname'] not in authenticDESTeams:
                    addAuthenticDESTeam(req['teamname'], req['password'])
                cursor.execute("update cred set SpiritFreed = 1 where Team = %s", (req['teamname'],))
                response = {'success': True}
            else:
                response = {'success': False}
        else:
            response = {'error': 'Invalid Credentials'}
        return json.dumps(response);
    except:
        logging.error(traceback.format_exc())
	response = {'error': 'There is some problem with the server'}
        return json.dumps(response)

# function to get DES encryption of plaintext
# inp: teamname, plaintext
# out: challenge string if plaitext is 'password', otherwise the ciphertext
def getDESEncryption(teamname, plaintext):
    if plaintext == 'password':
        cursor.execute("select Challenge from level4 where Team = %s", (teamname,))
        return cursor.fetchone()[0]
    else:
	return level4.desEncryption(plaintext, teamname)

# function to get EAEAE encryption of plaintext
# inp: teamname, plaintext
# out: challenge string if plaitext is 'password', otherwise the ciphertext
def getEAEAEEncryption(teamname, plaintext):
    if plaintext == 'password':
        cursor.execute("select Challenge from level5 where Team = %s", (teamname,))
        return cursor.fetchone()[0]
    else:
	return level5.eaeaeEncryption(plaintext, teamname)

# route to send DES encryption requests
# post parameters: teamname, password, plaintext
# post format: json
@app.route("/des", methods=['POST'])
def des():
    try:
        req = json.loads(stripNonASCII(request.data))
        if ('teamname' in req) and ('password' in req) and ('plaintext' in req):
	    if req['teamname'] in authenticDESTeams:
	        if authenticDESTeams[req['teamname']][0] == req['password']:
		    if MD5(req['plaintext']) == authenticDESTeams[req['teamname']][1]:
			cursor.execute("update cred set currentLevel = 4 where Team = %s and currentLevel = 3", (req['teamname'],))
                        cursor.execute("update level4 set CompletedAt = %s where Team = %s", (time.strftime('%Y-%m-%d %H:%M:%S'), req['teamname']))
                        if req['teamname'] not in authenticEAEAETeams:
                            addAuthenticEAEAETeam(req['teamname'], req['password'])
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
    except: # Exception, e:
        #print e
        logging.error(traceback.format_exc())
	response = {'error': 'There is some problem with the server'}
        return json.dumps(response)

# route to send EAEAE encryption requests
# post parameters: teamname, password, plaintext
# post format: json
@app.route("/eaeae", methods=['POST'])
def eaeae():
    try:
        req = json.loads(stripNonASCII(request.data))
        #print req;
        if ('teamname' in req) and ('password' in req) and ('plaintext' in req):
	    if req['teamname'] in authenticEAEAETeams:
	        if authenticEAEAETeams[req['teamname']][0] == req['password']:
		    if MD5(req['plaintext']) == authenticEAEAETeams[req['teamname']][1]:
			cursor.execute("update cred set currentLevel = 5 where Team = %s and currentLevel = 4", (req['teamname'],))
                        cursor.execute("update level5 set CompletedAt = %s where Team = %s", (time.strftime('%Y-%m-%d %H:%M:%S'), req['teamname']))
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
    except: # Exception, e:
        # print e.message
        # traceback.print_exc()
        logging.error(traceback.format_exc())
	response = {'error': 'There is some problem with the server'}
        return json.dumps(response)

# route to show stats to a client
# suppose the client is on currentLevel n, then he will only gets stats
# for levels <= n
# post parameters: teamname, password
# post format: json
@app.route("/stats", methods=['POST'])
def stats():
    try:
        req = json.loads(stripNonASCII(request.data))
        succ, level, d1, d2 = checkauth(req)
        if succ is True:
            cursor.execute("select Team, currentLevel from cred")
            results = cursor.fetchall();
            temp = [[], [], [], [], [], [], []]
            for item in results:
                if int(item[1]) > 0 and level >= 1:
                    temp[0].append(str(item[0]))
                if int(item[1]) > 1 and level >= 2:
                    temp[1].append(str(item[0]))
                if int(item[1]) > 2 and level >= 3:
                    temp[2].append(str(item[0]))
                if int(item[1]) > 3 and level >= 4:
                    temp[3].append(str(item[0]))
                if int(item[1]) > 4 and level >= 5:
                    temp[4].append(str(item[0]))
                if int(item[1]) > 5 and level >= 6:
                    temp[5].append(str(item[0]))
                if int(item[1]) > 6 and level >= 7:
                    temp[6].append(str(item[0]))
            data = map(lambda x : ', '.join (y for y in x), temp)
            response = {"stats": data}
        else:
            response = {'error': 'Invalid Credentials'}
        #print json.dumps(response);
        return json.dumps(response);
    except:
        logging.error(traceback.format_exc())
	response = {'error': 'There is some problem with the server'}
        return json.dumps(response)

# code for running through SSL
# context1 = ('server.crt', 'server.key')
# app.run(host='0.0.0.0', port=9999, threaded=True, ssl_context=context1)

#app.run(host='0.0.0.0', port=9999, threaded=True)

if __name__ == "__main__":
    app.run()
