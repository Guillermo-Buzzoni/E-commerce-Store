from flask import jsonify, render_template, request
from cs50 import SQL

db = SQL("sqlite:///database.db")

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

    base_query = """
        SELECT * FROM products 
        WHERE price BETWEEN ? AND ? 
    """

    try:
        # Optional category filter
        if category_id:
            base_query += "AND category_id = ? "
            products = db.execute(base_query + f"ORDER BY {sort_by} {order} LIMIT ? OFFSET ?", min_price, max_price, category_id, per_page, offset)
        else:
            products = db.execute(base_query + f"ORDER BY {sort_by} {order} LIMIT ? OFFSET ?", min_price, max_price, per_page, offset)
        
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(products), 200
        else:
            # return render_template('products.html', products=products)
            return render_template("products.html", products=products, page=page, per_page=per_page)
    except Exception as e:
        error_message = str(e)
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({"error": error_message}), 500
        else:
            return render_template('error.html', error=error_message), 500

def get_product(product_id):
    try:
        product = db.execute("SELECT * FROM products WHERE id = ?", product_id)
        if len(product) == 0:
            if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
                return jsonify({"error": "Product not found"}), 404
            else:
                return render_template('error.html', error="Product not found"), 404
        
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(product[0]), 200
        else:
            return render_template('product.html', product=product[0])
    except Exception as e:
        error_message = str(e)
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({"error": error_message}), 500
        else:
            return render_template('error.html', error=error_message), 500

def get_categories():
    """Fetch all product categories"""
    try:
        categories = db.execute("SELECT * FROM categories")
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(categories), 200
        else:
            return render_template('categories.html', categories=categories)
    except Exception as e:
        error_message = str(e)
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({"error": error_message}), 500
        else:
            return render_template('error.html', error=error_message), 500

def get_products_by_category(category_name):
    """Fetch products within a specific category"""
    try:
        category = db.execute("SELECT id FROM categories WHERE name = ?", category_name)
        if len(category) == 0:
            if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
                return jsonify({"error": "Category not found"}), 404
            else:
                return render_template('error.html', error="Category not found"), 404
        
        category_id = category[0]["id"]
        products = db.execute("SELECT * FROM products WHERE category_id = ?", category_id)
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(products), 200
        else:
            return render_template('products.html', products=products, category_name=category_name)
    except Exception as e:
        error_message = str(e)
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({"error": error_message}), 500
        else:
            return render_template('error.html', error=error_message), 500