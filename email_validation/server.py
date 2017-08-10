from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
app = Flask(__name__)
app.secret_key = 'secretsquirell'
mysql = MySQLConnector(app,'email_users')

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/validate', methods=['POST'])
def validate():
	session['email'] = request.form['email']
	print session['email']
	query = "select email from users"
	emails = mysql.query_db(query)
	#there must be a more efficient way to access values in a dictionary...
	mails = []
	for e in emails:
		mails += [e['email']]
	if EMAIL_REGEX.match(session['email']) == None:
		flash('Email is not valid!')
	elif session['email'] not in mails:
		return redirect('/success')
	else:
		flash("Email already in database.")
	return redirect('/')

@app.route('/success')
def success():
	query1 = "select email, created_at from users"
	emails = mysql.query_db(query1)
	if session:
		mails = []
		for e in emails:
			mails += [e['email']]
		if session['email'] not in mails:
			flash("Success! the email address you entered (" + session['email'] + ") is a VALID email address! Thank you!")
			query2 = "insert into users (email, created_at, updated_at) values (:email, now(), now())"
			data = {
				'email': session['email']
				}
			emails_to_add = mysql.query_db(query2, data)
	results = mysql.query_db(query1)
	return render_template('success.html', results = results)


@app.route('/delete/<del_email>')
def delete(del_email):
	query = "delete from users where email=:email"
	data = {
	'email': del_email
	}
	del_query = mysql.query_db(query, data)
	query_2 = "select * from users"
	allq = mysql.query_db(query_2)
	for i in allq:
		print i['email']
	session.clear()
	return redirect('/success')

app.run(debug=True)