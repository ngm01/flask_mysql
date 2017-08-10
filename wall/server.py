from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re, os, binascii, md5
app = Flask(__name__)
app.secret_key = 'nightswatch'
mysql = MySQLConnector(app,'wall')


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def home():
	try:
		if session['logged_in']:
			return redirect('/wall')
	except KeyError:
		return render_template('login.html')

@app.route('/wall')
def index():
	# all_users_query = "select * from users"
	# all_users_results = mysql.query_db(all_users_query)
	
	# for a in all_users_results:
	# 	for k,v in a.iteritems():
	# 		print str(k) + ': ' + str(v)
	
	#get db info about logged-in user
	user_id = session['logged_in']
	user_query = "select * from users where id=:id"
	user_data = {'id': user_id}
	user = mysql.query_db(user_query, user_data)



	#TODO: query db for messages
	msg_query = "select users.id, first_name, last_name, message, messages.id, messages.created_at from users join messages on messages.user_id = users.id"
	posts = mysql.query_db(msg_query)
	# for post in posts:
	# 	print post['first_name']

	comment_query = "select first_name, last_name, comment, comments.message_id, comments.created_at from comments join messages on message_id = messages.id join users on comments.user_id = users.id"
	comments = mysql.query_db(comment_query)
	for comment in comments:
		for k,v in comment.iteritems():
			print str(k) + ': ' + str(v)

	return render_template('index.html', user = user[0], posts = posts, comments = comments)

@app.route('/register', methods=['POST'])
def register():
	session['success'] = None
	email = request.form['reg_email']
	reg_query = "select email from users where email=:email"
	reg_query_data = {'email': email}
	req_query_result = mysql.query_db(reg_query, reg_query_data)
	print req_query_result
	if len(request.form['reg_email']) < 1 or EMAIL_REGEX.match(request.form['reg_email']) == None:
		flash("Please enter a valid email address.")
	if len(request.form['reg_fname']) < 1:
		flash("First name cannot be blank.")
		session['success'] = False
		# session['first_name'] = "notvalid"
	if len(request.form['reg_lname']) < 1:
		flash("Last name cannot be blank.")
		session['success'] = False
		# session['last_name'] = "notvalid"
	if len(request.form['reg_pword']) < 1:
		flash("Please enter a valid password.")
		session['success'] = False
	if request.form['reg_pword'] != request.form['confirm_pword']:
		flash("Password confirmation must match password.")
		session['success'] = False
	if req_query_result != []:
		flash("An account already exists for that email address.")
		session['success'] = False
	elif session['success'] != False:
		salt = binascii.b2a_hex(os.urandom(15))
		hashedword = md5.new(request.form['reg_pword'] + salt).hexdigest()
		
		insert_query = "insert into users (first_name, last_name, email, password, salt, created_at, updated_at) values (:first_name, :last_name, :email, :hash, :salt, now(), now()) "
		insert_data = {
		'first_name': request.form['reg_fname'],
		'last_name': request.form['reg_lname'],
		'email': email,
		'hash': hashedword,
		'salt': salt
		}
		new_id = mysql.query_db(insert_query, insert_data)
		
		session['logged_in'] = new_id
		return redirect('/wall')
	return redirect('/')

@app.route('/login', methods=['POST'])
def login():
	
	#check if user-supplied email exists in database
	logged_in_query = "select * from users where email=:email"
	email = request.form['login_email']
	password = request.form['login_pword']
	logged_in_data = {'email': email}
	logged_in_results = mysql.query_db(logged_in_query, logged_in_data)

	#Add error type parameter for flashed messages to display them in appropriate areas of the page
	if logged_in_results == []:
		flash("Please enter valid login credentials.")
	else:
		salt = logged_in_results[0]['salt']
		hash_check = md5.new(password + salt).hexdigest()
		if hash_check != logged_in_results[0]['password']:
	 		flash("Password incorrect.")
		else:
	 		session['logged_in'] = [logged_in_results[0]['id']]
	return redirect('/')

@app.route('/logout')
def logout():
	session.clear()
	return redirect('/')


@app.route('/post_message', methods=['POST'])
def post():
	user_id = session['logged_in']
	message = request.form['msg_box']
	if message != '':
		post_query = "insert into messages (user_id, message, created_at, updated_at) values (:user_id, :message, now(), now())"
		post_data = {
		'user_id': user_id,
		'message': message
		}
		insert_post = mysql.query_db(post_query, post_data)
	return redirect('/')

@app.route('/post_comment/<msg_id>', methods=['POST'])
def comment(msg_id):
	user_id = session['logged_in']
	comment = request.form['comment_box']
	if comment != '':
		comment_query = "insert into comments (user_id, message_id, comment, created_at, updated_at) values (:user_id, :message_id, :comment, now(), now())"
		comment_data = {
		'user_id': user_id,
		'message_id': msg_id,
		'comment': comment
		}
		print "hello"
		insert_comment = mysql.query_db(comment_query, comment_data)
	return redirect('/')


app.run(debug=True)