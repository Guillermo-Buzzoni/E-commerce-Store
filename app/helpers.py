from functools import wraps
from flask import session, jsonify

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "User not logged in"}), 401
        return f(*args, **kwargs)
    return decorated_function

def format_currency(value):
    """Format value as USD."""
    return f"${value:,.2f}"