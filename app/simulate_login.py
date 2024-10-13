from flask import jsonify, request, session
from werkzeug.security import check_password_hash
from cs50 import SQL

db = SQL("sqlite:///database.db")

# Simulate login for the given user credentials
def login_user(email, password):
    """Simulate login for user"""
    try:
        # Fetch user by email
        rows = db.execute("SELECT * FROM users WHERE email = ?", email)
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], password):
            return False

        # Remember the user in session
        session["user_id"] = rows[0]["id"]
        session["email"] = rows[0]["email"]
        return True
    except Exception as e:
        print(f"Error logging in: {e}")
        return False