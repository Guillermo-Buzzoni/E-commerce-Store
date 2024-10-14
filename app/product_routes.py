from flask import jsonify, render_template, request, url_for
from cs50 import SQL
from math import ceil

db = SQL("sqlite:///database.db")

def get_products():
    """Fetch products with pagination, filtering, and sorting"""
    category_id = request.args.get('category_id')
    min_price = request.args.get('min_price', type=float, default=0)
    max_price = request.args.get('max_price', type=float, default=999999999)
    sort_by = request.args.get('sort_by', 'name')
    order = request.args.get('order', 'asc')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    if sort_by not in ['name', 'price']:
        sort_by = 'name'
    if order not in ['asc', 'desc']:
        order = 'asc'
    
    offset = (page - 1) * per_page

    base_query = """
        SELECT p.*, pi.image_url 
        FROM products p
        LEFT JOIN (
            SELECT product_id, MIN(image_url) as image_url 
            FROM product_images 
            GROUP BY product_id
        ) pi ON p.id = pi.product_id
        WHERE p.price BETWEEN ? AND ? 
    """

    count_query = """
        SELECT COUNT(*) as total FROM products 
        WHERE price BETWEEN ? AND ? 
    """
    params = [min_price, max_price]

    if category_id:
        base_query += "AND category_id = ? "
        count_query += "AND category_id = ? "
        params.append(category_id)

    base_query += f"ORDER BY {sort_by} {order} LIMIT ? OFFSET ?"
    params.extend([per_page, offset])

    try:
        products = db.execute(base_query, *params)
        total_count = db.execute(count_query, *params[:-2])[0]['total']
        
        total_pages = ceil(total_count / per_page)
        
        categories = db.execute("SELECT * FROM categories")

        for product in products:
            if product['image_url']:
                product['image_url'] = url_for('static', filename=product['image_url'])

        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({
                'products': products,
                'page': page,
                'total_pages': total_pages,
                'total_count': total_count
            }), 200
        else:
            return render_template('products.html', 
                                   products=products,
                                   categories=categories,
                                   page=page,
                                   total_pages=total_pages,
                                   total_count=total_count,
                                   current_category=category_id,
                                   current_min_price=min_price,
                                   current_max_price=max_price,
                                   current_sort=sort_by,
                                   current_order=order)
    except Exception as e:
        error_message = str(e)
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({"error": error_message}), 500
        else:
            return render_template('error.html', error=error_message), 500

def get_product(product_id):
    try:
        product = db.execute("SELECT * FROM products WHERE id = ?", product_id)[0]
        product_images = db.execute("SELECT image_url FROM product_images WHERE product_id = ?", product_id)

        if not product:
            if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
                return jsonify({"error": "Product not found"}), 404
            else:
                return render_template('error.html', error="Product not found"), 404
        
        product['images'] = [url_for('static', filename=img['image_url']) for img in product_images]

        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(product), 200
        else:
            return render_template('product.html', product=product)
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