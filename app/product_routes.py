from flask import jsonify, render_template, request, url_for
from cs50 import SQL
from math import ceil

from review_routes import get_reviews, get_average_rating

db = SQL("sqlite:///database.db")

def get_products(category_id=None, min_price=None, max_price=None, sort_by=None, order=None, page=None, per_page=None, limit=None, is_deal=None, random=None):
    # If specific arguments are passed, use them. Otherwise, fall back to request.args.
    category_id = category_id if category_id is not None else request.args.get('category_id')
    min_price = min_price if min_price is not None else request.args.get('min_price', type=float, default=0)
    max_price = max_price if max_price is not None else request.args.get('max_price', type=float, default=float(1e9))
    sort_by = sort_by if sort_by is not None else request.args.get('sort_by', 'name')
    order = order if order is not None else request.args.get('order', 'asc')
    page = page if page is not None else int(request.args.get('page', 1))
    per_page = per_page if per_page is not None else request.args.get('per_page', type=int, default=12)
    
    # Prioritize function arguments for limit, is_deal, and random
    limit = limit if limit is not None else request.args.get('limit', type=int)
    is_deal = is_deal if is_deal is not None else request.args.get('is_deal', type=bool)
    random = random if random is not None else request.args.get('random', type=bool)

    query = """
        SELECT p.*, c.name as category_name 
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE p.price BETWEEN ? AND ?
    """
    params = [min_price, max_price]

    if category_id:
        query += " AND p.category_id = ?"
        params.append(category_id)

    if is_deal:
        query += " AND p.is_deal = 1"

    if random:
        query += " ORDER BY RANDOM()"
    else:
        # if sort_by == 'newest':
        #     query += " ORDER BY p.created_at DESC"
        # else:
        #     query += f" ORDER BY p.{sort_by} {order}"
        query += f" ORDER BY p.{sort_by} {order}"

    if limit:
        query += " LIMIT ?"
        params.append(limit)
    else:
        query += " LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])

    products = db.execute(query, *params)

    for product in products:
        images = db.execute("SELECT image_url FROM product_images WHERE product_id = ?", product['id'])
        product['images'] = [url_for('static', filename=img['image_url']) for img in images] if images else [url_for('static', filename='placeholder_img1.webp')]

    if request.endpoint == 'index':
        return products
    
    categories = db.execute("SELECT * FROM categories")
    
    count_query = """
        SELECT COUNT(*) as total
        FROM products p
        WHERE p.price BETWEEN ? AND ?
    """
    count_params = [min_price, max_price]

    if category_id:
        count_query += " AND p.category_id = ?"
        count_params.append(category_id)

    if is_deal:
        count_query += " AND p.is_deal = 1"

    total_count = db.execute(count_query, *count_params)[0]['total']
    total_pages = ceil(total_count / per_page)

    # Preserve the query params for pagination
    query_params = request.args.copy()
    query_params.pop('page', None)
    
    try:
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({
                'products': products,
                'categories': categories,
                'page': page,
                'total_pages': total_pages,
                'total_count': total_count,
                'per_page': per_page
            }), 200
        else:
            return render_template('products.html', 
                                   products=products,
                                   categories=categories,
                                   page=page,
                                   total_pages=total_pages,
                                   per_page=per_page,
                                   total_count=total_count,
                                   query_params=query_params,
                                   current_category=category_id,
                                   current_min_price=min_price,
                                   current_max_price=max_price,
                                   current_sort=sort_by,
                                   current_order=order,
                                   is_deal=is_deal)
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
        
        if product_images:
            product['images'] = [url_for('static', filename=img['image_url']) for img in product_images]
        else:
            product['images'] = [url_for('static', filename='placeholder_img1.webp')]

        reviews = get_reviews(product_id)

        average_rating = get_average_rating(product_id)

        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'product': product, 'reviews': reviews}), 200
        else:
            return render_template('product.html', product=product, reviews=reviews, average_rating=average_rating)
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