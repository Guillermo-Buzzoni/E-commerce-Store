-- Insert sample categories
INSERT OR
IGNORE INTO categories (name)
VALUES
    ('Electronics'),
    ('Books'),
    ('Clothing');

-- Insert sample products
INSERT OR
IGNORE INTO products (name, description, price, category_id, stock_quantity)
VALUES
    ('Smartphone', 'Latest model smartphone', 699.99, 1, 50),
    ('Laptop', 'High-performance laptop', 999.99, 1, 30),
    ('Novel', 'Bestselling novel', 19.99, 2, 100);

-- Insert sample product images
INSERT OR
IGNORE INTO product_images (product_id, image_url)
VALUES
    (1, 'fairphone5_img1.webp'),
    (1, 'fairphone5_img2.webp'),
    (2, 'laptop_img1.webp'),
    (2, 'laptop_img2.webp'),
    (3, 'novel_img1.webp');

-- Insert sample transactions
INSERT OR
IGNORE INTO transactions (user_id, total_amount)
VALUES
    (1, 719.98),
    (2, 1019.98);

-- Insert sample transaction items
INSERT OR
IGNORE INTO transaction_items (transaction_id, product_id, quantity, price_at_purchase)
VALUES
    (1, 1, 1, 699.99),
    (1, 3, 1, 19.99),
    (2, 2, 1, 999.99);

-- Insert sample reviews (only for products they purchased)
INSERT OR
IGNORE INTO reviews (user_id, product_id, rating, review_text)
VALUES
    (1, 1, 5, 'Excellent smartphone, highly recommend!'),
    (1, 3, 4, 'Interesting book, well written.'),
    (2, 2, 5, 'Amazing laptop for the price!');

-- Insert sample cart items
INSERT OR
IGNORE INTO cart_items (user_id, product_id, quantity)
VALUES
    (1, 1, 1),
    (2, 3, 2);