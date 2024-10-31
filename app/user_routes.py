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
        error = 'Password must contain at least 8 characters, including a letter, a number, and a special character'
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
        
        # Log the user in after successful registration
        user = db.execute("SELECT * FROM users WHERE email = ?", email)[0]
        session["user_id"] = user["id"]
        session["email"] = user["email"]
        
        success_message = 'User registered and logged in successfully'
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'success': success_message}), 201
        else:
            return redirect(url_for('index'))
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
                return render_template('login.html', error=error), 400

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
    user_id = session.get('user_id')

    if not user_id:
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'error': 'User not logged in'}), 401
        else:
            return redirect(url_for('login'))

    try:
        user = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]

        transactions = db.execute("""
            SELECT 
                t.id AS transaction_id, 
                t.transaction_date, 
                t.total_amount
            FROM transactions t
            WHERE t.user_id = ?
            ORDER BY t.transaction_date DESC
        """, user_id)

        for transaction in transactions:
            transaction_products = db.execute("""
                SELECT 
                    p.name AS product_name, 
                    ti.quantity, 
                    ti.price_at_purchase
                FROM transaction_items ti
                JOIN products p ON ti.product_id = p.id
                WHERE ti.transaction_id = ?
            """, transaction['transaction_id'])
            transaction['products'] = transaction_products

        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'user': user, 'transactions': transactions}), 200
        else:
            return render_template("profile.html", user=user, transactions=transactions)
    except Exception as e:
        error = str(e)
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({"error": error}), 500
        else:
            return render_template('error.html', error=error)