# E-commerce Store Project

This project is a simple e-commerce web application built with Flask, SQLite, and Bootstrap. It provides basic functionality for an online store, including product browsing, user authentication, shopping cart management, and checkout process.

## Features

- User registration and authentication
- Product browsing with categories
- Featured products and special deals
- Shopping cart functionality
- Checkout process
- Product reviews
- Responsive design

## Tech Stack

- Backend: Python with Flask
- Database: SQLite
- Frontend: HTML, CSS (Bootstrap), JavaScript
- Template Engine: Jinja2

## Project Structure

- `app.py`: Main application file with route definitions
- `setup.sql`: SQL script for database schema
- `templates/`:
  - `index.html`: Homepage template
  - `layout.html`: Base layout template
- (Other route files and templates not shown in the provided documents)

## Setup and Installation

1. Clone the repository:
   ```
   git clone [repository-url]
   cd [project-directory]
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```
   sqlite3 database.db < setup.sql
   ```

5. Run the application:
   ```
   flask run
   ```

6. Open a web browser and navigate to `http://localhost:5000`

## Usage

- Browse products on the homepage or through category pages
- Register for an account or log in
- Add products to your cart
- Proceed to checkout
- Leave reviews on products

## Acknowledgements

- CS50 library for SQLite database interaction
- Bootstrap for frontend styling
- Vectorportal.com for some of the images used in the project