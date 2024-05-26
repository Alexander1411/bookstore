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
   cd bookstore
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
- Added logging for debugging and monitoring purposes.

Logging
Configured logging to capture debug-level information:
```python
logging.basicConfig(level=logging.DEBUG)
```
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

Information system

Users
Types of Users: The system supports multiple user types, including regular users and an admin.
User Authentication: Users can register, log in, and log out, with credentials stored securely in the tbl_users table.
User Profiles: Users can update their profile information, including email, name, and address.

Data Requirements
Tables and Relationships: The system uses three main tables (tbl_users, books, and orders) with appropriate relationships defined using foreign keys.
Data Integrity: The use of primary keys ensures entity integrity, and foreign keys ensure referential integrity between tables.

Search
Book Search: Users can search for books by title. This functionality is handled by querying the books table based on user input.

Sorting
Sort Books: Books can be sorted by price, either in ascending or descending order. This is controlled by passing a sort parameter and modifying the SQL query accordingly.

Data Entry
User Registration: New users can register by providing necessary details, which are validated and then inserted into the tbl_users table.
Add Books to Inventory: Admin can add new books to the inventory via a form that inserts data into the books table.
Add Orders: Orders are created when users purchase books, inserting entries into the orders table.

Data Update
Update User Profile: Users can update their profile information, which updates the tbl_users table.
Update Book Inventory: Admin can update book inventory levels, modifying the books table.
Manage Cart: Users can add or remove books from their cart, which updates the inventory in the books table accordingly.

Validation
Input Validation: All user inputs are validated for required fields and appropriate formats before processing.
Example: Registration and profile updates check for required fields like username, password, email, name, and address.
Error Handling: The system includes try-except blocks to catch and handle errors during database operations, providing meaningful error messages to users.

Integrity
Entity Integrity: Each table has a primary key to uniquely identify records.
Referential Integrity: Foreign keys ensure that orders reference valid users and books.
Domain Integrity: Data types and constraints (e.g., decimal for price, varchar for strings) ensure valid data entries.

Reporting
Order History: Users can view their order history, which lists all orders with details like order date, book titles, quantities, and prices.
Admin Reports: Admin can view inventory levels and low stock alerts, which helps in managing the bookstore efficiently.