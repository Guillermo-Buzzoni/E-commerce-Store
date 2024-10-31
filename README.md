# E-commerce Store

#### Video demo: https://youtu.be/OkL456ybx9g

#### Description

This project is a web-based e-commerce application built with Python, Flask, and SQLite, styled with Bootstrap, and using Jinja2 templating for HTML rendering. The store simulates a complete e-commerce platform, allowing users to browse products, manage a cart, proceed to checkout, leave reviews, and view order history through an account profile. This project highlights the core functionality of an online store with simplicity in mind for database interaction, using the CS50 `SQL` library for its direct approach.

## Features

### User Management
- **Registration & Authentication**: Users can register, log in, log out, and view a profile containing order history.
- **Secure Passwords**: Passwords are hashed with `generate_password_hash` to ensure data security.

### Product Management
- **Product Browsing**: Users can view products by category and apply filters for price range, new arrivals, special deals, and keyword search to refine their selection.
- **Sorting Options**: Products can be sorted by price, name, or publication date, in either ascending or descending order.
- **Product Details**: Each product has its own page with a description, images, stock quantity, and price.
- **Reviews**: Verified buyers can leave reviews on products, which are displayed along with the product's average rating.

### Cart and Checkout
- **Add/Remove Items in Cart**: Users can add items, update quantities, and remove items from their cart.
- **Checkout Process**: The checkout process verifies stock availability and calculates the total purchase amount before creating a transaction record.

### Order History
- **Profile Page**: Users can view past transactions with detailed information on each purchase.
- **Review Tracking**: Users are able to review only products they have purchased, ensuring authenticity.

### Responsive Design
The application uses Bootstrap for mobile-friendly design, ensuring a smooth user experience across devices.

## Design Choices

### Database Interaction
To manage communication with the SQLite database, I chose the CS50 `SQL` library over more complex ORMs like SQLAlchemy. This decision was driven by the need to keep database handling straightforward, allowing more focus on implementing challenging aspects like user authentication, product filtering, and review logic. This choice reflects the project's educational goals and maintains a balance between simplicity and functionality.

### Folder Structure

- **`app.py`**: The main application file where routes are registered, the app is initialized, and database connections are managed.
- **`cart_routes.py`**: Handles routes for cart actions like adding, updating, and removing items, and managing the checkout process.
- **`helpers.py`**: Contains helper functions, including a decorator for checking login status and currency formatting.
- **`init_db.py`**: Script to initialize the database, create tables, and populate them with sample data (not required for running, as the `database.db` is uploaded directly).
- **`product_routes.py`**: Handles product-related routes for displaying products, filtering by category, sorting, and retrieving product details.
- **`review_routes.py`**: Manages product reviews, allowing users to add and view reviews.
- **`user_routes.py`**: Contains user registration, login, logout, and profile display routes.
- **`database.db`**: The SQLite database containing all necessary tables and sample data.
- **`requirements.txt`**: Lists required Python packages to run the application.
- **`setup.sql`**: SQL schema for creating tables and setting up constraints.

### Templates and Static Files

- **Templates**:
    - **`layout.html`**: Base template with a navbar, footer, and Bootstrap CSS for page structure.
    - **`index.html`**: Homepage template showcasing featured products and categories.
    - **`cart.html`**: Displays cart items and total price, with options to update item quantities.
    - **`checkout.html`**: Provides a summary of items being purchased and a button to confirm the order.
    - **`error.html`**: Template for displaying error messages.
    - **`product.html`**: Product details page with reviews, images, price, and add-to-cart functionality.
    - **`products.html`**: Page for viewing all products, with filters for category, price, and special deals.
    - **`profile.html`**: User profile page with order history.
    - **`register.html`** and **`login.html`**: Forms for user registration and login.
    - **`success.html`**: Displays success messages after certain actions, like completing a purchase.

- **Static Files**:
    - **`styles.css`**: For custom styles,
    - **Images**: Placeholder images and other assets used for product visuals.

## Database Structure

The database is structured to support the core functionality of the e-commerce store:

- **Users**: Contains user details such as `email`, `password`, and registration timestamp. Passwords are stored securely using hashing.
- **Products**: Stores product information including `name`, `description`, `price`, stock quantity, and category. This table links to `categories` to facilitate browsing by category.
- **Categories**: Maintains a list of product categories, allowing users to browse products by specific categories.
- **Product Images**: Associates multiple images with each product, enhancing product display on the frontend.
- **Cart Items**: Temporarily stores items added to the cart by each user. These entries are removed once the user checks out.
- **Transactions**: Logs completed purchases with the `user_id` and total amount spent. This links to `transaction_items` for a breakdown of each purchase.
- **Transaction Items**: Details individual items within a transaction, capturing the `product_id`, quantity, and price at the time of purchase.
- **Reviews**: Stores product reviews submitted by users, including `rating`, `review_text`, and timestamps.

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

4. Run the application:
   ```
   flask run
   ```

5. Access the Application:

   Open a web browser and navigate to `http://localhost:5000`

## Acknowledgements

- **CS50 library** for SQLite database interaction
- **Bootstrap** for frontend styling
- **Vectorportal.com** for some of the images used in the project