import re
from cs50 import SQL
from flask import Flask, jsonify, request, session
from flask_session import Session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "User not logged in"}), 401
        return f(*args, **kwargs)
    return decorated_function

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

if __name__ == '__main__':
    
    with app.test_request_context():
        # Simulate user login before starting the server
        success = login_user("test1@example.com", "Password1!")
        if success:
            print("User test1@example.com logged in successfully!")
        else:
            print("Login failed for test1@example.com.")
    
    # Run the app
    # app.run(debug=True, use_reloader=True)
    app.run(debug=True)
    




# Register route
@app.route('/api/register', methods=['POST'])
def register():
    # Get JSON data from request body
    data = request.get_json()

    # Extract the email, password, and confirmation from the JSON
    email = data.get('email')
    password = data.get('password')
    confirmation = data.get('confirmation')

    # Email validation (basic format check)
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'error': 'Invalid email format'}), 400

    # Password validation (min 8 characters, one letter, one number, one special character)
    if len(password) < 8 or not re.search(r'[A-Za-z]', password) or not re.search(r'[0-9]', password) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return jsonify({'error': 'Password must be at least 8 characters long, contain one letter, one number, and one special character'}), 400

    # Password confirmation validation
    if password != confirmation:
        return jsonify({'error': 'Passwords do not match'}), 400
    
    try:
        # Check if email already exists
        rows = db.execute("SELECT * FROM users WHERE email = ?", email)
        if len(rows) > 0:
            return jsonify({"error": "Email already in use"}), 400

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        # Insert the new user into the database
        db.execute("INSERT INTO users (email, password) VALUES (?, ?)", email, hashed_password)

        return jsonify({'success': 'User registered successfully'}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
# Login route
@app.route('/api/login', methods=['POST'])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # Get JSON data from request body
    data = request.get_json()

    # Extract the email and password from the JSON
    email = data.get('email')
    password = data.get('password')

    # Check if both fields are provided
    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400

    try:
        # Fetch the user from the database
        rows = db.execute("SELECT * FROM users WHERE email = ?", email)
        if len(rows) != 1:
            return jsonify({'error': 'Invalid email or password'}), 400

        user = rows[0]

        # Verify the password
        if not check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid email or password'}), 400
        
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["email"] = rows[0]["email"]

        # For simplicity, let's just return a success message
        return jsonify({'success': 'Login successful'}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Logout route
@app.route('/api/logout', methods=['POST'])
def logout():
    """Log user out"""

    # Clear the session
    session.clear()

    return jsonify({'success': 'Logout successful'}), 200


# Fetch all products
@app.route('/api/products', methods=['GET'])
def get_products():
    """Fetch products with pagination, filtering, and sorting"""
    category_id = request.args.get('category_id')
    min_price = request.args.get('min_price', 0)
    max_price = request.args.get('max_price', 999999)
    sort_by = request.args.get('sort_by', 'price')
    order = request.args.get('order', 'asc')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    offset = (page - 1) * per_page

    # Base query
    query = """
        SELECT * FROM products 
        WHERE price BETWEEN ? AND ? 
    """

    # Optional category filter
    if category_id:
        query += "AND category_id = ? "
        products = db.execute(query + f"ORDER BY {sort_by} {order} LIMIT ? OFFSET ?", min_price, max_price, category_id, per_page, offset)
    else:
        products = db.execute(query + f"ORDER BY {sort_by} {order} LIMIT ? OFFSET ?", min_price, max_price, per_page, offset)
    
    return jsonify(products), 200


# Fetch a specific product by ID
@app.route('/api/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Fetch a single product by ID"""
    try:
        product = db.execute("SELECT * FROM products WHERE id = ?", product_id)
        if len(product) == 0:
            return jsonify({"error": "Product not found"}), 404
        return jsonify(product[0]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/product/<int:product_id>/review', methods=['POST'])
@login_required
def add_review(product_id):
    """Add a review for a product"""
    data = request.get_json()
    user_id = session.get('user_id')
    rating = data.get('rating')
    review_text = data.get('review_text')

    # Validate data
    if not rating or not review_text or int(rating) not in range(1, 6):
        return jsonify({"error": "Invalid rating or review"}), 400

    # Ensure the user has purchased this product
    purchase_check = db.execute(
        "SELECT 1 FROM transaction_items "
        "JOIN transactions ON transactions.id = transaction_items.transaction_id "
        "WHERE transactions.user_id = ? AND transaction_items.product_id = ?",
        user_id, product_id
    )
    if len(purchase_check) == 0:
        return jsonify({"error": "You must purchase the product to leave a review"}), 403

    # Insert the review
    try:
        db.execute(
            "INSERT INTO reviews (user_id, product_id, rating, review_text) VALUES (?, ?, ?, ?)",
            user_id, product_id, rating, review_text
        )
        return jsonify({"message": "Review added successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Fetch all reviews for a product
@app.route('/api/product/<int:product_id>/reviews', methods=['GET'])
def get_reviews(product_id):
    """Fetch reviews for a product"""
    try:
        reviews = db.execute("SELECT * FROM reviews WHERE product_id = ?", product_id)
        return jsonify(reviews), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Fetch all categories
@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Fetch all product categories"""
    try:
        categories = db.execute("SELECT * FROM categories")
        return jsonify(categories), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Fetch products by category
@app.route('/api/category/<category_name>', methods=['GET'])
def get_products_by_category(category_name):
    """Fetch products within a specific category"""
    try:
        category = db.execute("SELECT id FROM categories WHERE name = ?", category_name)
        if len(category) == 0:
            return jsonify({"error": "Category not found"}), 404
        category_id = category[0]["id"]
        
        products = db.execute("SELECT * FROM products WHERE category_id = ?", category_id)
        return jsonify(products), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Cart management: fetch (GET) or add item to cart (POST)
@app.route('/api/cart', methods=['GET', 'POST'])
@login_required
def manage_cart():
    """Fetch or update the user's cart"""

    user_id = session["user_id"]

    if request.method == 'GET':
        try:
            # Fetch cart items for the user
            cart_items = db.execute("SELECT * FROM cart_items WHERE user_id = ?", user_id)
            return jsonify(cart_items), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    if request.method == 'POST':
        try:
            data = request.get_json()
            product_id = data.get("product_id")
            quantity = data.get("quantity")

            if not product_id or not quantity:
                return jsonify({"error": "Product ID and quantity required"}), 400

            # Add item to cart or update quantity if it already exists
            db.execute(
                "INSERT INTO cart_items (user_id, product_id, quantity) VALUES (?, ?, ?) "
                "ON CONFLICT(user_id, product_id) DO UPDATE SET quantity = quantity + ?",
                user_id, product_id, quantity, quantity
            )
            return jsonify({"message": "Item added to cart"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route('/api/checkout', methods=['POST'])
@login_required
def checkout():
    """Checkout and record the transaction"""
    data = request.get_json()

    # Get user_id from session
    user_id = session.get("user_id")
    
    cart_items = data.get('cart_items')

    # Validate the data
    if not cart_items:
        return jsonify({"error": "Missing cart items"}), 400

    try:
        total_amount = 0  # Initialize total amount

        # Begin transaction: Insert into transactions table
        transaction_id = db.execute(
            "INSERT INTO transactions (user_id, total_amount) VALUES (?, 0)",
            user_id
        )
        print(f"Transaction ID created: {transaction_id}")
        
        # Loop through each cart item
        for item in cart_items:
            product_id = item.get('product_id')
            quantity = item.get('quantity')

            # Fetch product details (price and stock)
            product = db.execute("SELECT price, stock_quantity FROM products WHERE id = ?", product_id)
            if len(product) == 0 or product[0]['stock_quantity'] < quantity:
                return jsonify({"error": f"Not enough stock for product {product_id}"}), 400

            # Calculate price for this item and add to total
            item_price = product[0]['price']
            total_amount += item_price * quantity

            # Insert transaction item
            db.execute(
                "INSERT INTO transaction_items (transaction_id, product_id, quantity, price_at_purchase) "
                "VALUES (?, ?, ?, ?)",
                transaction_id, product_id, quantity, item_price
            )
            print(f"Inserted transaction item for product {product_id}, quantity {quantity}")

            # Deduct stock
            db.execute(
                "UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?",
                quantity, product_id
            )
            print(f"Updated stock for product {product_id}, deducted {quantity}")

        # Update total_amount in the transactions table
        db.execute(
            "UPDATE transactions SET total_amount = ? WHERE id = ?",
            total_amount, transaction_id
        )
        print(f"Updated total amount for transaction {transaction_id}: {total_amount}")

        # Clear cart after successful checkout
        db.execute("DELETE FROM cart_items WHERE user_id = ?", user_id)
        print(f"Cleared cart for user {user_id}")

        return jsonify({"message": "Transaction completed successfully!", "total_amount": total_amount}), 200

    except Exception as e:
        print(f"Error during checkout: {e}")
        return jsonify({"error": str(e)}), 500


# @app.route('/api/checkout', methods=['POST'])
# @login_required
# def checkout():
#     """Checkout and record the transaction"""
#     data = request.get_json()

#     # Get user_id from session or request
#     user_id = session.get("user_id")
    
#     cart_items = data.get('cart_items')
#     total_amount = data.get('total_amount')

#     # Validate the data
#     if not cart_items or not total_amount:
#         return jsonify({"error": "Missing cart items or total amount"}), 400

#     try:
#         # Start transaction: Insert into transactions table
#         transaction_id = db.execute(
#             "INSERT INTO transactions (user_id, total_amount) VALUES (?, ?)",
#             user_id, total_amount
#         )
#         print(f"Transaction ID created: {transaction_id}")
        
#         # Loop through each cart item
#         for item in cart_items:
#             product_id = item.get('product_id')
#             quantity = item.get('quantity')

#             # Fetch product stock
#             product = db.execute("SELECT stock_quantity FROM products WHERE id = ?", product_id)
#             if len(product) == 0 or product[0]['stock_quantity'] < quantity:
#                 return jsonify({"error": f"Not enough stock for product {product_id}"}), 400

#             # Insert transaction item
#             db.execute(
#                 "INSERT INTO transaction_items (transaction_id, product_id, quantity, price_at_purchase) "
#                 "VALUES (?, ?, ?, (SELECT price FROM products WHERE id = ?))",
#                 transaction_id, product_id, quantity, product_id
#             )
#             print(f"Inserted transaction item for product {product_id}, quantity {quantity}")

#             # Deduct stock
#             db.execute(
#                 "UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?",
#                 quantity, product_id
#             )
#             print(f"Updated stock for product {product_id}, deducted {quantity}")

#         # Clear cart after successful checkout
#         db.execute("DELETE FROM cart_items WHERE user_id = ?", user_id)
#         print(f"Cleared cart for user {user_id}")

#         return jsonify({"message": "Transaction completed successfully!"}), 200

#     except Exception as e:
#         print(f"Error during checkout: {e}")
#         return jsonify({"error": str(e)}), 500