Bookstore Web Application

Project Overview
This project is a web application for a bookstore, allowing users to register, log in, browse books, manage a shopping cart, purchase books, and manage their profile. It also includes an admin section for managing book inventory.

Table of Contents
1. Installation
2. Configuration
3. Routes and Features
4. Project Progression
5. Logging
6. Security
7. Acknowledgements
8. Information system

Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/Alexander1411/bookstore.git
   cd bookstore/
   ```
2. Install the required Python packages:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up MySQL database with the following configuration:
   ```sql
   CREATE DATABASE bookstore_users;
   ```
Configuration
1. Update the MySQL configuration in the `routes.py` file:
   ```python
   app.config["MYSQL_HOST"] = "10.0.0.4"
   app.config["MYSQL_USER"] = "remote_user"
   app.config["MYSQL_PASSWORD"] = "alexander"
   app.config["MYSQL_DB"] = "bookstore_users"
   ```
2. Set a secret key for session management:
   ```python
   app.secret_key = 'supersecretkey'
   ```
Routes and Features

Home
Route: `/`
Method: GET
Description: Displays the homepage.

User Authentication
Login
Route: `/login`
Methods: GET, POST
Description: Allows users to log in.

Register
Route: `/register`
Methods: GET, POST
Description: Allows new users to register.

Logout
Route: `/logout`
Method: GET
Description: Logs out the user.

User Profile
View Profile
Route: `/profile`
Method: GET
Description: Displays the users profile and order history.

Edit Profile
Route: `/edit_profile`
Methods: GET, POST
Description: Allows users to update their profile information.

Book Browsing and Shopping Cart
Browse Books
Route: `/books`
Method: GET
Description: Displays available books with sorting options

Add to Cart
Route: `/add_to_cart/<int:book_id>`
Method: GET
Description: Adds a book to the shopping cart.

Remove from Cart
Route: `/remove_from_cart/<int:book_id>`
Method: GET
Description: Removes a book from the shopping cart.

View Cart
Route: `/cart`
Method: GET
Description: Displays the contents of the shopping cart.

Clear Cart
Route: `/clear_cart`
Method: GET
Description: Clears the entire shopping cart.

Purchase
Purchase Books
Route: `/purchase`
Methods: GET, POST
Description: Handles the purchase of books from the cart.

Buy Book Directly
Route: `/buy_book/<int:book_id>`
Method: POST
Description: Directly buys a single book.

Orders
View Orders
Route: `/view_orders`
Method: GET
Description: Displays the user's order history.

Admin
Inventory Management
Route: `/admin/inventory`
Method: GET
Description: Allows the admin to view and manage book inventory.

Update Inventory
Route: `/update_inventory/<int:book_id>`
Method: POST
Description: Allows the admin to update the inventory of a book.

Project Progression
### Initial Setup
- Created Flask application.
- Configured MySQL database connection.
- Implemented basic routes for home, login, and register.

### User Authentication
- Implemented user registration and login functionality.
- Stored session data for logged-in users.

### User Profile and Orders
- Added user profile view displaying personal information and order history.
- Implemented order history retrieval for logged-in users.

### Book Browsing and Shopping Cart
- Created a book browsing page with sorting options.
- Implemented functionality to add and remove books from the shopping cart.
- Displayed low stock alerts for books with less than 5 items in stock.

### Purchase and Order Management
- Implemented cart purchase functionality.
- Added functionality for users to directly buy a book.
- Ensured order details are stored and user balance is updated.

### Admin Features
- Created an admin inventory management page.
- Allowed the admin to update book inventory.

### Security and Improvements
- Enhanced password management.

Security
1. Updated the MySQL password, ensuring better security:
   ```python
   app.config["MYSQL_PASSWORD"] = "alexander"
   ```
2. Implemented session management with a secret key to secure user sessions.

Acknowledgements
- Flask documentation for providing a robust framework.
- MySQL for database management.
- Flask-MySQLdb for seamless database integration.
- Flask-CORS for handling cross-origin requests.
- Community and contributors for their support and feedback.
