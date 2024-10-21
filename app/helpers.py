from functools import wraps
from flask import jsonify, redirect, request, session, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
                return jsonify({"error": "User not logged in"}), 401
            else:
                return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def format_currency(value):
    """Format value as USD."""
    return f"${value:,.2f}"