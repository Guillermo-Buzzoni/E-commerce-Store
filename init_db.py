# import sqlite3

# def init_db():
#     with sqlite3.connect('database.db') as conn:
#         with open('setup.sql', 'r') as f:
#             conn.executescript(f.read())
#         with open('generateSampleData.sql', 'r') as f:
#             conn.executescript(f.read())

#     print("Database initialized!")

# if __name__ == "__main__":
#     init_db()

from cs50 import SQL
from werkzeug.security import generate_password_hash
import os

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
    
    # Insert users with hashed passwords
    insert_users_with_hashed_passwords(db)
    
    # Execute generateSampleData.sql
    execute_sql_file(db, 'generateSampleData.sql')
    
    print("Database initialized!")

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

def insert_users_with_hashed_passwords(db):
    users = [
        {"email": "test1@example.com", "password": "Password1!"},
        {"email": "test2@example.com", "password": "Password2!"},
        {"email": "test3@example.com", "password": "Password3!"}
    ]

    for user in users:
        hashed_password = generate_password_hash(user['password'])
        try:
            db.execute(
                "INSERT OR IGNORE INTO users (email, password) VALUES (?, ?)",
                user['email'],
                hashed_password
            )
            print(f"Successfully added user: {user['email']}")
        except Exception as e:
            print(f"Error adding user {user['email']}: {e}")

if __name__ == "__main__":
    init_db()