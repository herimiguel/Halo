from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import md5
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = 'ThisIsSecret'
mysql = MySQLConnector(app, 'halodb')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/Register', methods = ['POST'])
def register():
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    email = request.form['email']
    password = md5.new(request.form['password']).hexdigest()
    data = {
        'firstName': firstName,
        'lastName': lastName,
        'email': email,
        'password': password
    }
    errors =True
    query = 'select * from users where email = :email'
    db_check = mysql.query_db(query, data)
    print 'CHECKING DATA'
    #checking if user is already in db
    if len(db_check) == 1:
        flash("THIS EMAIL IS ALREADY REGISTERED. PLEASE LOG IN")
    # VALIDATION AND ERROR MESSAGES
    elif len(firstName) < 1 or len(lastName) < 1 or len(email) < 1 or len(request.form['password']) < 1: 
        flash(" fields are required!")
    elif not EMAIL_REGEX.match(email):
        flash("Invalid Email Address!")
    else:
        errors = False
    # if not in database and no errors, update database, set session id 
    if errors:
        return redirect('/')
    else:
        insert = 'insert into users (firstName, lastName, email, password, created_at, updated_at) values(:firstName, :lastName, :email, :password, NOW(), NOW())'
        session['id'] = mysql.query_db(insert, data)
        return redirect('/success')

@app.route('/login', methods = ['POST'])
def login():
    email = request.form['email']
    password = md5.new(request.form['password']).hexdigest()
    data = {
        'email': email,
        'password': password
    }
    errors = True
    query = 'select * from users where email = :email'
    db_check = mysql.query_db(query, data)
    # Validations and error messages
    if not EMAIL_REGEX.match(email):
        flash("INVALID EMAIL ADDRESS!")
    elif len(db_check) != 1:
        flash("Email address is not Registered! Please Register an account")
    elif len(email) < 1 or len(request.form['password']) < 1:
        flash("Email and Password fields are required")
    elif db_check[0]['password'] != password:
        flash("Incorrect password, Try again")
    else:
        errors = False
    #No errors, set Session Id and Login 
    if errors:
        return  redirect('/')
    else:
        session['id'] = db_check[0]['id']
        return redirect('/success')

@app.route('/success')
def success():
    user_id = session['id']
    query = 'SELECT firstName, lastName, id from users where users.id = :user_id '
    data = {
        'user_id': user_id,
        }
    user_name = mysql.query_db(query, data)
    firstName = user_name[0]['firstName']
    lastName = user_name[0]['lastName']
    query1 = 'SELECT id, note, user_id from notes where notes.user_id = :user_id '
    all_notes = mysql.query_db(query1, data)
    return render_template('success.html', firstName= firstName, lastName= lastName, user_id = user_id, all_notes = all_notes)        
       

@app.route('/createNote', methods = ['POST'])
def createNote():
    note= request.form['note']
    user_id = session['id']
    data = {
        'user_id' : user_id,
        'note': note
    }
    errors = True
    # query = 'select id from users where users.id = :user_id '
    if len(note) <1:
        flash("Note field is required!")
    else:
        errors = False
    if errors:
        return redirect('/success')
    else:
        insert = "insert into notes (note, created_at, updated_at, user_id ) values (:note, NOW(), NOW(), :user_id)"
        mysql.query_db(insert, data)
    return redirect('/success')


@app.route('/removeNote/<id>')
def delete(id):
    query = "DELETE FROM notes WHERE id = :id"
    data = {'id': id}
    mysql.query_db(query, data)
    return redirect('/success')

@app.route('/logout')
def logout():
    session.clear()
    return redirect ('/')    
                
app.run(debug=True)        
