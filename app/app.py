from cs50 import SQL
from flask import Flask, render_template
from flask_session import Session
from helpers import format_currency

from cart_routes import manage_cart, checkout, add_to_cart, remove_from_cart, update_cart_item
from product_routes import get_products, get_product, get_categories, get_products_by_category
from review_routes import add_review, get_reviews
from user_routes import login, logout, profile, register

db = SQL("sqlite:///database.db")

# App initialization
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Register custom filter
app.jinja_env.filters['format_currency'] = format_currency

# Caching headers
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# User management routes
app.add_url_rule('/login', view_func=login, methods=['GET', 'POST'])
app.add_url_rule('/logout', view_func=logout, methods=['GET', 'POST'])
app.add_url_rule('/profile', view_func=profile, methods=['GET'])
app.add_url_rule('/register', view_func=register, methods=['GET', 'POST'])

# Product management routes
app.add_url_rule('/products', view_func=get_products, methods=['GET'])
app.add_url_rule('/product/<int:product_id>', view_func=get_product, methods=['GET'])
app.add_url_rule('/categories', view_func=get_categories, methods=['GET'])
app.add_url_rule('/category/<category_name>', view_func=get_products_by_category, methods=['GET'])

# Cart and checkout routes
app.add_url_rule('/cart', view_func=manage_cart, methods=['GET', 'POST'])
app.add_url_rule('/cart/add', view_func=add_to_cart, methods=['POST'])
app.add_url_rule('/cart/remove', view_func=remove_from_cart, methods=['POST'])
app.add_url_rule('/cart/update', view_func=update_cart_item, methods=['POST'])
app.add_url_rule('/checkout', view_func=checkout, methods=['GET', 'POST'])

# Review routes
app.add_url_rule('/product/<int:product_id>/review', view_func=add_review, methods=['GET', 'POST'])
app.add_url_rule('/product/<int:product_id>/reviews', view_func=get_reviews, methods=['GET'])

@app.route('/')
def index():
    featured_products = get_products(limit=4, random=True)
    categories = db.execute("SELECT * FROM categories")
    deals = get_products(limit=3, is_deal=True)

    return render_template('index.html', featured_products=featured_products, categories=categories, deals=deals)

if __name__ == '__main__':
    app.run(debug=True)