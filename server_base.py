from flask import Flask
from flask import render_template, request as req, session, g as gFunc, url_for, flash, get_flashed_messages, redirect
import sqlite3
import json
import sys, os
from colorama import *
import sys

from passlib.hash import sha256_crypt
from contextlib import closing

#Terminal text colours
green = Fore.GREEN
red = Fore.RED
yellow = Fore.YELLOW
bright = Style.BRIGHT

debug = True
init( autoreset = True )


if (debug):

	def success( string ):
		print(green + bright + "[+] " + string)

	def error( string ):
		sys.stderr.write(red + bright + "[-] " + string + "\n" )

	def warning( string ):
		print(yellow + "[!] " + string)

else:
	def success( string ): pass
	def error( string ): pass
	def warning( string ): pass

# ============================================================

DB = '$DB'
SETTINGS = '$SETTINGS'
CERTIFICATE = '$CERT'
PRIVATE_KEY = '$PRIVKEY'

SECRET_KEY = 'sessionVariable'

if DB == '$DB':
	error("DB file is missing!")
	exit(-1)

if SETTINGS == '$SETTINGS':
	error("Setting File is missing!")
	exit(-1)

if CERTIFICATE == '$CERT':
	error("Certificate file is missing!")
	exit(-1)

if PRIVATE_KEY == '$PRIVKEY':
	error("Private key is missing!")
	exit(-1)

app = Flask( __name__ )

app.config.from_object(__name__)

requiredSettings = [
	"appTitle", "appAbout", "appNavigationLoggedOut",
	"appNavigationLoggedIn", "tasks"
]

if not ( os.path.exists(SETTINGS) ):
	error("The setting file '" + SETTINGS + "' does not seem to exist!")
	exit(-1)
else:
	success("The setting file found!")
	handle = open( SETTINGS )
	setting = json.loads(handle.read().replace("\n","").replace("\t",""))
	try:
		for requiredSetting in requiredSettings:
			assert setting[requiredSetting]
	except Exception as e:	
		error("setting file '" + sys.argv[1] + "' is missing the following setting tag:")
		warning(e.message)
		error("Fix the error & run the server again")
		exit(-1)
	
	handle.close()

	success("The settings seem fine!")
	success("Starting the server..")
	
def init_db():
	with closing(connect_db()) as db:
	    with app.open_resource(app.config['DB'], mode='r') as f:
	        db.cursor().executescript(f.read())
	    db.commit()

def connect_db():
	return sqlite3.connect( app.config['DB'] )

@app.before_request
def before_request():
    gFunc.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(gFunc, 'db', None)
    if db is not None:
        db.close()

def render( template_name, **kwargs ):
	return render_template( template_name, 
							appTitle = setting['appTitle'], 
							appNavigationLoggedOut = setting['appNavigationLoggedOut'],
							appNavigationLoggedIn = setting['appNavigationLoggedIn'],
							**kwargs
						   )

@app.route("/login", methods=["GET", "POST"])
def login():

	error = ""
	if req.method == "POST":

		cursor = gFunc.db.execute('select username, password from users')
		# username, password_hash
		users = dict(( row[0], row[1] ) for row in cursor.fetchall())

		if not req.form['username'] in users.keys():
			error = 'Username does not exist!'
		else:

			if not ( sha256_crypt.verify( req.form['password'], users[req.form['username']] ) ):
				error = "Incorrect password!"
			else:
				
				sessionLogin( req.form['username'] )

				return redirect( "tasks" )

	return render( 'login.html', error = error )


@app.route("/register", methods=["GET", "POST"])
def register():

	cursor = gFunc.db.execute('select username from users')
	
	usernames = [row[0] for row in cursor.fetchall() ]

	error = ""
	if req.method == "POST":

		if (req.form['username']) in usernames:
			error = 'Username already taken!'
		elif (req.form['password'] == ""):
			error = "Please enter a password!"
		elif req.form['password'] != req.form['confirm']:
			error = 'Incorrect password!'
		else:

			cursor = gFunc.db.execute('insert into users (username, password, solvedTasks, totalPoints, prevSubmission) values ( ?, ?, ?, ?, ? )', [ 
				               req.form['username'], 
				               sha256_crypt.encrypt( req.form['password']),
				               "",  # No tasks completed
				               0,   # no totalPoints.
				               0,   # and no previous submission time.
				  ] )

			gFunc.db.commit()


			flash("Hi " + req.form['username'] + ", you've successfully signed up!")
			sessionLogin( req.form['username'] )
			return redirect( "tasks" )

	return render( 'register.html', error = error )


@app.route("/scoreboard")
def scoreboard(): 

	cursor = gFunc.db.execute('select username, totalPoints from users order by totalPoints desc, prevSubmission asc')	
	response = cursor.fetchall()	
	
	users = [ { "username": row[0], "totalPoints": row[1] } for row in response]
	
	return render("scoreboard.html", users = users )

@app.route("/logout")
def logout():

	sessionLogout()
	return redirect("about")

@app.route("/")
@app.route("/about")
def about(): return render("about.html", appAbout=setting['appAbout'])

@app.route("/tasks")
def tasksPage(): 
	if not ( session['loggedIn'] ):
		return render("login.html", error = "Only registered users can view tasks!")	
	return render("tasks.html", tasks = setting['tasks'])

@app.route("/checkAnswer", methods=["GET", "POST"])
def checkAnswer(): 

	if req.method == "POST":
		if req.form['taskID'] in session['solvedTasks'].split():

			return json.dumps({'correct': -1});

		correctAnswers = setting['tasks'][int(req.form['taskID'])]["possibleAnswers"]

		if ( req.form['answer'] in correctAnswers ):

			newSolvedTasks = session['solvedTasks'] + " " +req.form['taskID']
			newTotalPoints = int(session['totalPoints']) + setting['tasks'][int(req.form['taskID'])]["points"]
			cursor = gFunc.db.execute("update users set solvedTasks = (?), totalPoints = (?), prevSubmission = (SELECT strftime('%s')) where username = (?)", [
					newSolvedTasks,
					newTotalPoints, 
					session['username']
				] );

			session['totalPoints'] = newTotalPoints
			session['solvedTasks'] = newSolvedTasks
			gFunc.db.commit();

			return json.dumps({'correct': 1, 'newTotalPoints': newTotalPoints});
		else:
			return json.dumps({'correct': 0});

def sessionLogin( username ):
	
	flash("You were successfully logged in!")

	cursor = gFunc.db.execute('select solvedTasks, totalPoints from users where username = (?)',
			[username])	

	solvedTasks, totalPoints = cursor.fetchone()

	session['loggedIn'] = True
	session['username'] = username
	session['solvedTasks'], session['totalPoints'] = solvedTasks, totalPoints

def sessionLogout():

	flash("Logging out completed.")

	session['loggedIn'] = False
	session.pop('username')
	session.pop('totalPoints')

def prepareTasks():

	for i in range(len( setting['tasks'])):
		task = setting['tasks'][i]
		task["id"] = str(i)
 
if ( __name__ == "__main__" ):

	prepareTasks()
	context = (CERTIFICATE, PRIVATE_KEY)
	app.run( host="0.0.0.0", debug=False, ssl_context=context, port = 2000, threaded = True )
	#app.run( host="0.0.0.0", debug=False, port = 2000, threaded = True )

