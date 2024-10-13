import re
from flask import jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from cs50 import SQL
from helpers import login_required


db = SQL("sqlite:///database.db")

def register():
    """Registers a new user"""
    if request.method == 'GET':
        return render_template('register.html')
    
    data = request.form if request.form else request.get_json()
    email = data.get('email')
    password = data.get('password')
    confirmation = data.get('confirmation')

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        error = 'Invalid email format'
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'error': error}), 400
        else:
            return render_template('register.html', error=error), 400
        
    if len(password) < 8 or not re.search(r'[A-Za-z]', password) or not re.search(r'[0-9]', password) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        error = 'Password must meet complexity requirements'
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'error': error}), 400
        else:
            return render_template('register.html', error=error), 400
        
    if password != confirmation:
        error = 'Passwords do not match'
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'error': error}), 400
        else:
            return render_template('register.html', error=error), 400
    
    try:
        rows = db.execute("SELECT * FROM users WHERE email = ?", email)
        if rows:
            error = "Email already in use"
            if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
                return jsonify({"error": error}), 400
            else:
                return render_template('register.html', error=error), 400

        hashed_password = generate_password_hash(password)
        db.execute("INSERT INTO users (email, password) VALUES (?, ?)", email, hashed_password)
        success_message = 'User registered successfully'
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'success': success_message}), 201
        else:
            return render_template('login.html', message=success_message), 201
    except Exception as e:
        error = str(e)
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({"error": error}), 500
        else:
            return render_template('error.html', error=error), 500
    
def login():
    """Log the user in"""
    if request.method == 'GET':
        return render_template('login.html')
    
    session.clear()
    data = request.form if request.form else request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        error = 'Missing email or password'
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'error': error}), 400
        else:
            return render_template('login.html', error=error), 400

    try:
        rows = db.execute("SELECT * FROM users WHERE email = ?", email)
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], password):
            error = 'Invalid email or password'
            if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
                return jsonify({'error': error}), 400
            else:
                return render_template('login.html', error=error), 400 # login.html has nowhere to show the error

        session["user_id"] = rows[0]["id"]
        session["email"] = rows[0]["email"]
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'success': 'Login successful'}), 200
        else:
            return redirect(url_for('index'))
    except Exception as e:
        error = str(e)
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({"error": error}), 500
        else:
            return render_template('error.html', error=error), 500

def logout():
    """Log the user out"""
    session.clear()
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify({'success': 'Logout successful'}), 200
    else:
        return redirect(url_for('index'))
    
@login_required
def profile():
    """Display user profile"""
    user_id = session.get("user_id")
    try:
        user = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]
        return render_template('profile.html', user=user)
    except Exception as e:
        return render_template('error.html', error=str(e))