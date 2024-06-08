from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import sqlite3
import os

app = Flask(__name__) #flask is a class, and app is an instance in flask. __name__ is special variable in python that holds the name of current module
app.secret_key = 'your_secret_key'  # Needed for flash messages and session management, like when password is wrong or username is wrong

DATABASE = 'users.db' #your database where password and username exists

app.config['SESSION_PERMANENT'] = False  # Ensure the session cookie expires when the browser closes

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row #Establishes a connection to the SQLite database and returns the connection object. The row_factory attribute is set to sqlite3.Row to access columns by name.
    return conn

def init_db():
    if not os.path.exists(DATABASE): #using os to see if database named users.db is there
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        print('Database initialized!')

@app.route('/') #routes to whatever specific url is in brackets, / takes us to the root url
def home(): #checking if username is in session and running, if not takes to login page
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')  # This renders your existing index.html

@app.route('/login', methods=['GET', 'POST']) #get and give data to/from login 
def login():
    if request.method == 'POST': #in post method data is encrypted in get its not encrypted
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                            (username, password)).fetchone() #check if username and password is it in database
        conn.close()
        
        if user: #if true
            session['username'] = username
            session.permanent = False  # Ensure the session cookie expires when the browser closes and logging back in
            flash('Login successful!', 'success')
            return render_template('index.html')  # Redirect to the home page after successful login
        else:
            flash('Invalid username or password', 'danger')
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            flash('Account created successfully! You can now log in.', 'success') #creates account and redirects back to login page
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already taken. Please choose another one.', 'danger')
        finally:
            conn.close()
            
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/assets/<path:filename>') #accessing assets
def custom_static(filename):
    return send_from_directory('assets', filename)


@app.after_request #function inside flask to execute after aa request is made
def after_request(response):
    session.pop('username', None) #using pop method to remove username so that user must login everytime website is closed
    return response

if __name__ == "__main__": #main function
    init_db() #initialze the db
    app.run(debug=True)