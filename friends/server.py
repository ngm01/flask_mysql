from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
app = Flask(__name__)
app.secre_key = 'secretsquirell'
mysql = MySQLConnector(app,'full_friends')

@app.route('/')
def index():
	query = "select * from friends"
	friends = mysql.query_db(query)
	return render_template('index.html', all_friend = friends)
	render_template('index.html')


@app.route('/friends', methods=['POST'])
def create():
	#add a friend to the database
	#write query as a string
	query = "insert into friends (first_name, last_name, age, created_at, updated_at) values (:first_name, :last_name, :age, now(), now())"

	split_name = request.form['name'].split(' ')

	if request.form['name'] != '' and request.form['age'] != '':

		print "here it is", request.form['name']
		print "here it is", request.form['age']
		if len(split_name) > 1:
			data = {
				'first_name': split_name[0],
				'last_name': split_name[1],
				'age': request.form['age'],
			}

		else:
			data = {
				'first_name': request.form['name'],
				'last_name': '',
				'age': request.form['age'],
			}

		mysql.query_db(query, data)
	return redirect('/')

app.run(debug=True)