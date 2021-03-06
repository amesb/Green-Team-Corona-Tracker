'''
authorizatin code from flask tutorial
https://flask.palletsprojects.com/en/2.0.x/tutorial/views/
© Copyright 2010 Pallets
Modified for EOU CS362 Corona Virus project
'''

import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Register new Account

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        passwordHash = request.form['password']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not passwordHash:
            error = 'Password is required.'
        elif db.execute(
            'SELECT username FROM Users WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = f"{username} is already registered. Please choose " \
                    f"another username"

        if error is None:
            db.execute(
                'INSERT INTO Users (username, passwordHash,firstName, lastName, isInfected, isAdmin) VALUES (?, ?, ?, ?, ?, ?)',
                (username, generate_password_hash(passwordHash), firstName, lastName, False, False)
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

# Login

@bp.route('/login', methods=('GET', 'POST'))
def login():


    if request.method == 'POST':
        username = request.form['username']
        passwordHash = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM Users WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['passwordHash'], passwordHash):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user'] = user['username']
            # send to test user index
            return redirect(url_for("test_user_index.tux"))


        flash(error)

    return render_template('auth/login.html')



@bp.before_app_request
def load_logged_in_user():
    # changed from tutorial, was originally userid instead of username
    userName = session.get('user')

    if userName is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM Users WHERE username = ?', (userName,)
        ).fetchone()

# logout

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


'''login required'''
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view