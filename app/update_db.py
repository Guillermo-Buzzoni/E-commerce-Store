from cs50 import SQL
from init_db import generate_password_hash

# Correct path to the database
db = SQL("sqlite:///c:/Users/guill/OneDrive/Documentos/GitHub/ecommerce/database.db")

def update_user_passwords(num_users):
    """Update passwords for demo users"""
    for i in range(num_users):
        email = f"user{i+1}@example.com"
        new_password = generate_password_hash(f"Password{i+1}!")
        db.execute("UPDATE users SET password = ? WHERE email = ?", new_password, email)
    print(f"Updated passwords for {num_users} users")

if __name__ == '__main__':
    print("Updating passwords for demo users...")
    update_user_passwords(100)