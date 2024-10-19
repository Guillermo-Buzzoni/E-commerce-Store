import os
import random

from cs50 import SQL
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Database file path
DB_FILE = "database.db"

def init_db():
    # Create an empty database file if it doesn't exist
    if not os.path.exists(DB_FILE):
        open(DB_FILE, 'w').close()
    
    # Initialize the database connection
    db = SQL(f"sqlite:///{DB_FILE}")
    
    # Execute setup.sql
    execute_sql_file(db, 'setup.sql')

    # Generate sample data
    generate_users(db, 100)
    generate_categories_and_products(db)
    generate_transactions(db)
    generate_reviews(db)
    generate_cart_items(db)
    
    print("Database initialized with sample data!")

def execute_sql_file(db, filename):
    with open(filename, 'r') as f:
        sql_script = f.read()
        # Split the script into individual statements
        statements = sql_script.split(';')
        for statement in statements:
            if statement.strip():
                try:
                    db.execute(statement)
                except Exception as e:
                    print(f"Error executing statement from {filename}: {e}")
                    print(f"Problematic statement: {statement}")

def generate_users(db, num_users):
    for i in range(num_users):
        email = f"user{i+1}@example.com"
        # password = generate_password_hash(f"password{i+1}")
        password = generate_password_hash(f"Password{i+1}!")
        db.execute("INSERT INTO users (email, password) VALUES (?, ?)", email, password)
    print(f"Generated {num_users} users")

def generate_categories_and_products(db):
    categories = [
        {"name": "Electronics", "products": [
            "Smartphone", "Laptop", "Tablet", "Smart Watch", "Wireless Earbuds",
            "Bluetooth Speaker", "Power Bank", "Fitness Tracker", "Digital Camera", "Gaming Console",
            "Smart TV", "VR Headset", "Drone", "Portable Charger", "E-Reader",
            "Smart Home Hub", "Wireless Mouse", "Mechanical Keyboard", "External Hard Drive", "USB Flash Drive",
            "Noise Cancelling Headphones", "Smart Light Bulb", "Smart Thermostat", "Smart Doorbell", "Smart Lock",
            "Smart Plug", "Smart Security Camera", "Smart Smoke Detector", "Smart Water Leak Sensor", "Smart Garage Door Opener"
        ]},
        {"name": "Home & Kitchen", "products": [
            "Coffee Maker", "Blender", "Toaster Oven", "Air Fryer", "Robot Vacuum",
            "Instant Pot", "Stand Mixer", "Food Processor", "Microwave", "Kettle",
            "Slow Cooker", "Rice Cooker", "Electric Grill", "Juicer", "Espresso Machine",
            "Dishwasher", "Refrigerator", "Freezer", "Washing Machine", "Dryer",
            "Vacuum Cleaner", "Steam Mop", "Iron", "Air Purifier", "Dehumidifier",
            "Humidifier", "Space Heater", "Fan", "Air Conditioner", "Water Filter"
        ]},
        {"name": "Fashion", "products": [
            "T-Shirt", "Jeans", "Sneakers", "Dress", "Jacket",
            "Sunglasses", "Watch", "Backpack", "Scarf", "Hat",
            "Belt", "Wallet", "Handbag", "Earrings", "Necklace",
            "Bracelet", "Ring", "Shoes", "Boots", "Sandals",
            "Socks", "Underwear", "Swimsuit", "Gloves", "Beanie",
            "Cap", "Tie", "Bow Tie", "Cufflinks", "Pocket Square"
        ]},
        {"name": "Books", "products": [
            "Fiction Novel", "Cookbook", "Self-Help Book", "Biography", "Science Fiction",
            "Mystery Thriller", "History Book", "Children's Book", "Poetry Collection", "Travel Guide",
            "Graphic Novel", "Comic Book", "Textbook", "Reference Book", "Art Book",
            "Photography Book", "Journal", "Notebook", "Planner", "Diary",
            "Encyclopedia", "Dictionary", "Thesaurus", "Manual", "Guidebook",
            "Anthology", "Short Story Collection", "Essay Collection", "Memoir", "Autobiography"
        ]},
        {"name": "Sports & Outdoors", "products": [
            "Yoga Mat", "Dumbbells", "Running Shoes", "Tent", "Hiking Backpack",
            "Bicycle", "Sleeping Bag", "Basketball", "Tennis Racket", "Camping Stove",
            "Fishing Rod", "Kayak", "Paddleboard", "Surfboard", "Skateboard",
            "Roller Skates", "Scooter", "Helmet", "Life Jacket", "Climbing Gear",
            "Golf Clubs", "Soccer Ball", "Football", "Baseball Bat", "Hockey Stick",
            "Snowboard", "Ski Poles", "Ice Skates", "Water Bottle", "Fitness Tracker"
        ]}
    ]

    for category in categories:
        category_id = db.execute("INSERT INTO categories (name) VALUES (?)", category["name"])
        for product_name in category["products"]:
            price = round(random.uniform(9.99, 999.99), 2)
            stock_quantity = random.randint(0, 100)
            is_deal = random.choice([0, 1])
            
            product_id = db.execute("""
            INSERT INTO products (name, description, price, category_id, stock_quantity, is_deal)
            VALUES (?, ?, ?, ?, ?, ?)
            """, product_name, f"High-quality {product_name.lower()} for your needs", price, category_id, stock_quantity, is_deal)
            
            # Generate 1-3 images for each product
            num_images = random.randint(1, 3)
            for i in range(num_images):
                db.execute("INSERT INTO product_images (product_id, image_url) VALUES (?, ?)",
                           product_id, f"product_{product_id}_img{i+1}.webp")

    print("Generated categories, products, and product images")

def generate_transactions(db):
    users = db.execute("SELECT id FROM users")
    products = db.execute("SELECT id, price FROM products")
    
    for user in users:
        num_transactions = random.randint(0, 5)
        for _ in range(num_transactions):
            transaction_date = datetime.now() - timedelta(days=random.randint(1, 365))
            transaction_id = db.execute("INSERT INTO transactions (user_id, total_amount, transaction_date) VALUES (?, 0, ?)",
                                        user['id'], transaction_date)
            
            num_items = random.randint(1, 5)
            total_amount = 0
            for _ in range(num_items):
                product = random.choice(products)
                quantity = random.randint(1, 3)
                price_at_purchase = product['price']
                total_amount += price_at_purchase * quantity
                
                db.execute("INSERT INTO transaction_items (transaction_id, product_id, quantity, price_at_purchase) VALUES (?, ?, ?, ?)",
                           transaction_id, product['id'], quantity, price_at_purchase)
            
            db.execute("UPDATE transactions SET total_amount = ? WHERE id = ?", total_amount, transaction_id)

    print("Generated transactions and transaction items")

def generate_reviews(db):
    transactions = db.execute("SELECT DISTINCT user_id, product_id FROM transactions JOIN transaction_items ON transactions.id = transaction_items.transaction_id")
    
    for transaction in transactions:
        if random.random() < 0.7:  # 70% chance of leaving a review
            rating = random.randint(1, 5)
            review_text = f"{'Very disappointing' if rating == 1 else 'Needs improvement' if rating == 2 else 'Average product' if rating == 3 else 'Good product' if rating == 4 else 'Excellent product'}! {'Would not recommend.' if rating <= 2 else 'Might buy again.' if rating == 3 else 'Recommended!' if rating == 4 else 'Highly recommended!'}"
            db.execute("INSERT INTO reviews (user_id, product_id, rating, review_text) VALUES (?, ?, ?, ?)",
                       transaction['user_id'], transaction['product_id'], rating, review_text)

    print("Generated reviews")

def generate_cart_items(db):
    users = db.execute("SELECT id FROM users")
    products = db.execute("SELECT id FROM products")
    
    for user in users:
        if random.random() < 0.3:  # 30% chance of having items in cart
            num_items = random.randint(1, 5)
            for _ in range(num_items):
                product = random.choice(products)
                quantity = random.randint(1, 3)
                db.execute("INSERT OR IGNORE INTO cart_items (user_id, product_id, quantity) VALUES (?, ?, ?)",
                           user['id'], product['id'], quantity)

    print("Generated cart items")

if __name__ == "__main__":
    init_db()