# BOTCOPY/src/App/route.py

from flask import Blueprint, render_template, request, redirect, url_for, session

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if 'logged_in' in session and session['logged_in']:
        return render_template('index.html')
    else:
        return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Giả sử có một username và password cố định cho mục đích demo
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            return redirect(url_for('main.index'))
        else:
            error = 'Invalid Credentials. Please try again.'
            return render_template('login.html', error=error)
    return render_template('login.html')

@main.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('main.login'))
