from cs50 import SQL
from datetime import datetime
from flask import jsonify, request, session, render_template, redirect, url_for
from helpers import login_required

db = SQL("sqlite:///database.db")

@login_required
def add_review(product_id):
    if request.method == 'GET':
        return render_template('add_review.html', product_id=product_id)

    data = request.form if request.form else request.get_json()
    user_id = session.get('user_id')
    rating = data.get('rating')
    review_text = data.get('review_text')

    # Validate data
    if not rating or not review_text or int(rating) not in range(1, 6):
        error = "Invalid rating or review"
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({"error": error}), 400
        else:
            return render_template('error.html', error=error), 400

    # Ensure the user has purchased this product
    purchase_check = db.execute(
        "SELECT 1 FROM transaction_items "
        "JOIN transactions ON transactions.id = transaction_items.transaction_id "
        "WHERE transactions.user_id = ? AND transaction_items.product_id = ?",
        user_id, product_id
    )
    if len(purchase_check) == 0:
        error = "You must purchase the product to leave a review"
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({"error": error}), 403
        else:
            return render_template('error.html', error=error), 403

    # Insert the review
    try:
        db.execute(
            "INSERT INTO reviews (user_id, product_id, rating, review_text) VALUES (?, ?, ?, ?)",
            user_id, product_id, rating, review_text
        )
        success_message = "Review added successfully!"
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({"message": success_message}), 201
        else:
            return render_template('success.html', message=success_message), 201
            # return redirect(url_for('product.html', product_id=product_id))
            # return render_template('product.html', product=product, reviews=reviews, average_rating=average_rating, error=error)

    except Exception as e:
        error = str(e)
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({"error": error}), 500
        else:
            return render_template('error.html', error=error), 500

def get_reviews(product_id):
    """Fetch reviews for a product"""
    try:
        reviews = db.execute("SELECT * FROM reviews WHERE product_id = ?", product_id)
        for review in reviews:
            if isinstance(review['created_at'], str):
                review['created_at'] = datetime.strptime(review['created_at'], "%Y-%m-%d %H:%M:%S") # review this. Does it make sense?
        return reviews
        return reviews
    except Exception as e:
        raise Exception(f"Error fetching reviews: {str(e)}")
        
def get_average_rating(product_id):
    result = db.execute("SELECT AVG(rating) as avg_rating FROM reviews WHERE product_id = ?", product_id)
    return result[0]['avg_rating'] if result[0]['avg_rating'] else None