from flask import jsonify, redirect, render_template, request, session, url_for
from cs50 import SQL
from helpers import login_required

db = SQL("sqlite:///database.db")

@login_required
def manage_cart():
    """Fetch or update the user's cart"""
    user_id = session["user_id"]

    # if not user_id:
    #     return redirect(url_for('login'))
    
    if request.method == 'GET':
        try:
            cart_items = db.execute("""
                SELECT c.product_id, p.name as product_name, p.price, c.quantity
                FROM cart_items c
                JOIN products p ON c.product_id = p.id
                WHERE c.user_id = ?
            """, user_id)
            
            total = sum(item['price'] * item['quantity'] for item in cart_items)
            
            if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
                return jsonify(cart_items), 200
            else:
                return render_template('cart.html', cart_items=cart_items, total=total), 200
        except Exception as e:
            error = str(e)
            if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
                return jsonify({"error": error}), 500
            else:
                return render_template('error.html', error=error), 500

    if request.method == 'POST':
        try:
            data = request.form if request.form else request.get_json()
            product_id = data.get("product_id")
            quantity = data.get("quantity")

            if not product_id or not quantity:
                error = "Product ID and quantity required"
                if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
                    return jsonify({"error": error}), 400
                else:
                    return render_template('error.html', error=error), 400

            db.execute(
                "INSERT INTO cart_items (user_id, product_id, quantity) VALUES (?, ?, ?) "
                "ON CONFLICT(user_id, product_id) DO UPDATE SET quantity = quantity + ?",
                user_id, product_id, quantity, quantity
            )
            success_message = "Item added to cart"
            if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
                return jsonify({"message": success_message}), 201
            else:
                return redirect(url_for('manage_cart'))
        except Exception as e:
            error = str(e)
            if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
                return jsonify({"error": error}), 500
            else:
                return render_template('error.html', error=error), 500


@login_required
def update_cart_item():
    """Update the quantity of an item in the cart"""
    user_id = session["user_id"]
    item_id = request.form.get("item_id")
    new_quantity = request.form.get("quantity", type=int)

    if not item_id or new_quantity is None:
        return jsonify({"error": "Missing item_id or quantity"}), 400

    try:
        db.execute("UPDATE cart_items SET quantity = ? WHERE id = ? AND user_id = ?", 
                   new_quantity, item_id, user_id)
        return redirect(url_for('manage_cart'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@login_required
def remove_from_cart():
    """Remove an item from the cart"""
    user_id = session["user_id"]
    item_id = request.form.get("item_id")

    if not item_id:
        return jsonify({"error": "Missing item_id"}), 400

    try:
        db.execute("DELETE FROM cart_items WHERE id = ? AND user_id = ?", item_id, user_id)
        return redirect(url_for('manage_cart'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@login_required
def checkout():
    """Checkout and record the transaction"""
    user_id = session["user_id"]
    
    if request.method == 'GET':
        try:
            cart_items = db.execute("""
                SELECT c.product_id, p.name as product_name, p.price, c.quantity
                FROM cart_items c
                JOIN products p ON c.product_id = p.id
                WHERE c.user_id = ?
            """, user_id)
            
            total = sum(item['price'] * item['quantity'] for item in cart_items)
            
            return render_template('checkout.html', cart_items=cart_items, total=total)
        except Exception as e:
            error = str(e)
            return render_template('error.html', error=error), 500
    
    if request.method == 'POST':
        try:
            cart_items = db.execute("""
                SELECT c.product_id, p.name as product_name, p.price, c.quantity, p.stock_quantity
                FROM cart_items c
                JOIN products p ON c.product_id = p.id
                WHERE c.user_id = ?
            """, user_id)

            if not cart_items:
                error = "Your cart is empty"
                return render_template('error.html', error=error), 400

            total_amount = 0
            transaction_id = db.execute("INSERT INTO transactions (user_id, total_amount) VALUES (?, 0)", user_id)
            
            for item in cart_items:
                if item['stock_quantity'] < item['quantity']:
                    error = f"Not enough stock for product {item['product_name']}"
                    return render_template('error.html', error=error), 400

                item_total = item['price'] * item['quantity']
                total_amount += item_total

                db.execute(
                    "INSERT INTO transaction_items (transaction_id, product_id, quantity, price_at_purchase) "
                    "VALUES (?, ?, ?, ?)", transaction_id, item['product_id'], item['quantity'], item['price']
                )

                db.execute(
                    "UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?",
                    item['quantity'], item['product_id']
                )

            db.execute("UPDATE transactions SET total_amount = ? WHERE id = ?", total_amount, transaction_id)
            db.execute("DELETE FROM cart_items WHERE user_id = ?", user_id)

            success_message = "Transaction completed successfully!"
            return render_template('success.html', message=success_message, total_amount=total_amount), 200
        except Exception as e:
            error = str(e)
            return render_template('error.html', error=error), 500

# @login_required
# def checkout():
#     """Checkout and record the transaction"""
#     if request.method == 'GET':
#         return render_template('checkout.html')
    
#     data = request.form if request.form else request.get_json()
#     user_id = session.get("user_id")
#     cart_items = data.get('cart_items')

#     if not cart_items:
#         error = "Missing cart items"
#         if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
#             return jsonify({"error": error}), 400
#         else:
#             return render_template('error.html', error=error), 400
#     try:
#         total_amount = 0
#         transaction_id = db.execute("INSERT INTO transactions (user_id, total_amount) VALUES (?, 0)", user_id)
        
#         for item in cart_items:
#             product_id = item.get('product_id')
#             quantity = item.get('quantity')

#             product = db.execute("SELECT price, stock_quantity FROM products WHERE id = ?", product_id)
            
#             if len(product) == 0 or product[0]['stock_quantity'] < quantity:
#                 error = f"Not enough stock for product {product_id}"
#                 if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
#                     return jsonify({"error": error}), 400
#                 else:
#                     return render_template('error.html', error=error), 400

#             item_price = product[0]['price']
#             total_amount += item_price * quantity

#             db.execute(
#                 "INSERT INTO transaction_items (transaction_id, product_id, quantity, price_at_purchase) "
#                 "VALUES (?, ?, ?, ?)", transaction_id, product_id, quantity, item_price
#             )

#             db.execute(
#                 "UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?",
#                 quantity, product_id
#             )

#         db.execute("UPDATE transactions SET total_amount = ? WHERE id = ?", total_amount, transaction_id)
#         db.execute("DELETE FROM cart_items WHERE user_id = ?", user_id)

#         success_message = "Transaction completed successfully!"
#         if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
#             return jsonify({"message": success_message, "total_amount": total_amount}), 200
#         else:
#             return render_template('success.html', message=success_message, total_amount=total_amount), 200
#     except Exception as e:
#         error = str(e)
#         if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
#             return jsonify({"error": error}), 500
#         else:
#             return render_template('error.html', error=error), 500