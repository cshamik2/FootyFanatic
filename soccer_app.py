from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key

def user_exists(username):
    with open('users.txt', 'r') as file:
        users = file.readlines()
        for user in users:
            uname, _ = user.strip().split(',')
            if uname == username:
                return True
    return False

def register_user(username, password):
    with open('users.txt', 'a') as file:
        hashed_password = generate_password_hash(password)
        file.write(f"{username},{hashed_password}\n")

def fetch_recent_matches():
    url = 'http://api.football-data.org/v4/competitions/PL/matches?status=FINISHED'
    headers = {'X-Auth-Token': '67865b93b6774cd9a1ef1b9b6c2d1ee9'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        matches = response.json().get('matches', [])[:5]  # Get only the last 5 matches
        news_items = []
        for match in matches:
            print(match)
            news_items.append(match)
        return news_items
    else:
        print("Failed to fetch matches:", response.status_code)
        return []

@app.route('/')
def home():
    return render_template('index.html')
 
@app.route('/matches')
def matches():
    news = fetch_recent_matches()
    return render_template('matches.html', news=news)

@app.route('/teams')
def teams():
    return render_template('teams.html')  

@app.route('/scores')
def scores():
    return render_template('scores.html')  

@app.route('/article/<int:id>')
def article(id):
    return render_template(f'article{id}.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not user_exists(username):
            register_user(username, password)
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists. Choose a different one.', 'error')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_user(username, password):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials', 'error')
    return render_template('login.html')

def check_user(username, password):
    with open('users.txt', 'r') as file:
        users = file.readlines()
        for user in users:
            uname, pwd = user.strip().split(',')
            if uname == username and check_password_hash(pwd, password):
                return True
    return False

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)

