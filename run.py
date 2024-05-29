from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL, MySQLdb
from flask_cors import CORS
from decimal import Decimal
import datetime
import random
import string
import logging

app = Flask(__name__)
CORS(app)
app.secret_key = 'supersecretkey' # Set the secret key for session management

# MySQL Configuration
app.config["MYSQL_HOST"] = "10.0.0.4"  # my VM IP
app.config["MYSQL_USER"] = "remote_user"
app.config["MYSQL_PASSWORD"] = "alexander"  # explain how password was changed (High pressure)
app.config["MYSQL_DB"] = "bookstore_users"

mysql = MySQL(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route("/")
def home():
    return render_template("index.html")  # Used this for python tutorials https://realpython.com/

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':  # sets session variables after checking credentials, 
        username = request.form['username'] # Retrieve
        pwd = request.form['password'] # Retrieve
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # cursor for the database
        try:
            # Execute a query to find the user by username
            cur.execute("SELECT * FROM tbl_users WHERE username = %s", (username,)) # REFERENCE https://stackoverflow.com/questions/70585322/i-cant-find-the-correct-syntax-for-select-from
            user = cur.fetchone() # Fetch the user record
        except Exception as e: # If occurs
            cur.close()
            return render_template("login.html", error="An error occurred: " + str(e))
        cur.close()
        if user and pwd == user['password']:
            session["username"] = user['username']
            session["user_id"] = user['id']
            session.pop('cart', None)  # Clear any existing cart on new login
            return redirect(url_for("user_profile"))
        else:
            # Render the login page with an error message if credentials are invalid
            return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")
# REFERENCE https://flask.palletsprojects.com/en/2.0.x/tutorial/views/#the-login-view | This helped me undertand how to handle user login, session management, and error handling.

@app.route('/register', methods=['GET', 'POST']) # 
def register():
    if request.method == 'POST': # Check if the request method is POST
        username = request.form['username'] # Retrieve
        pwd = request.form['password'] # Retrieve
        email = request.form['email'] # Retrieve
        name = request.form['name'] # Retrieve
        address = request.form['address'] # Retrieve
        
        # Checks if any of the required fields are missing
        if not username or not pwd or not email or not name or not address:
            flash('All fields are required!', 'danger') # Notification
            return redirect(url_for('register'))
        
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # Create a cursor for the database
        try:
             # New user into the tbl_users table
            cur.execute("INSERT INTO tbl_users (username, password, email, name, address) VALUES (%s, %s, %s, %s, %s)", 
                        (username, pwd, email, name, address))
            mysql.connection.commit() # Commit the transaction to save changes
        except Exception as e:
            cur.close()
            return render_template("register.html", error="An error occurred: " + str(e))
        cur.close()
        return redirect(url_for('login'))
    return render_template('register.html')
# REFERENCE https://github.com/Arunodhaya/Register-using-Flask - Found this repository, code for handling user registration, validating input fields, and inserting new users into a MySQL 
# Reference: https://www.youtube.com/watch?v=Z1RJmh_OqeA - Watched a tutorial on creating a registration form in Flask, helped me.

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    session.pop('cart', None)  # Ensure the cart is cleared on logout
    return redirect(url_for('home'))
#Reference: https://stackoverflow.com/questions/25331249/flask-login-log-out-user - Had a read on how to handle user logout in Flask,

@app.route('/profile')
def user_profile():
    if 'username' not in session: # Check 
        return redirect(url_for('login'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM tbl_users WHERE id = %s", (session['user_id'],)) # Retrieve the user's details from the database
    user = cur.fetchone() # Fetch the user record
    cur.close()

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # Create anotherone
    cur.execute("""
        SELECT o.po_number, o.order_date, b.title, o.quantity, b.price
        FROM orders o
        JOIN books b ON o.book_id = b.id
        WHERE o.user_id = %s AND o.po_number IS NOT NULL AND o.po_number != 'N/A'
        ORDER BY o.order_date DESC
    """, (session['user_id'],)) # Retrieve the user's order history from the database
    orders = cur.fetchall() # Fetch all order records
    cur.close()

    return render_template('profile.html', user=user, orders=orders)
#REFERENCE: https://github.com/MMansy19/Flask-User-Profile-Management - Used his example of managing user profiles, including retrieving user details and related orders from a database
#REFERENCE: https://www.youtube.com/watch?v=CSHx6eCkmv0 - This helped me on how to implement user authentication and profile management in app.run.

@app.route('/books')
def books_page():
    sort_by = request.args.get('sort_by', 'price_asc') # Get the sorting order from the request, default to 'price_asc' (Previously missed/forgotten)
    query = request.args.get('query', '') #Get the search query from the request, default to an empty string

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    if query: # Check if there is a search query
        search_query = f"%{query}%"  # Format the search query for a SQL LIKE clause
        cur.execute("SELECT * FROM books WHERE title LIKE %s ORDER BY price ASC", (search_query,))  # Execute a query to find books that match the search/sorted by price ascending
    else:
        if sort_by == 'price_desc': # Check the sorting order and execute the appropriate query
            cur.execute("SELECT * FROM books ORDER BY price DESC") # Sort books by price descending
        else:
            cur.execute("SELECT * FROM books ORDER BY price ASC") # Sort books by price asc
    
    books = cur.fetchall()
    cur.close()

    for book in books: # Iterate through the list of books
        if book['inventory'] < 5: # If the less than 5
            flash(f"Low stock alert: Only {book['inventory']} left of '{book['title']}'", 'warning')
    
    return render_template('books.html', books=books, sort_by=sort_by, query=query)
#REFERENCE: https://www.youtube.com/watch?v=cYWiDiIUxQc - Helped me by covering CRUD operations in Flask with SQLAlchemy (I used the similar logic), including how to query and filter data from a database
#REFERENCE: https://www.youtube.com/watch?v=CSHx6eCkmv0 - Looked at querying databases, and rendering templates, helped me

@app.route('/add_to_cart/<int:book_id>')
def add_to_cart(book_id):
    if 'username' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT inventory FROM books WHERE id = %s", (book_id,)) # Retrieve the books inventory from the database
        inventory = cur.fetchone()['inventory']
        if inventory < 1: # Checks if the book is out of stock
            flash('This book is out of stock.', 'danger')
            return redirect(url_for('books_page'))
        cur.execute("UPDATE books SET inventory = inventory - 1 WHERE id = %s", (book_id,)) # Decrease the books inventory by 1
        mysql.connection.commit() # Commit the transaction to save changes

        if 'cart' not in session: # Check if the cart is not in the session
            session['cart'] = {} # Initialise an empty cart in the session
        cart = session['cart']
        book_id_str = str(book_id) # Convert book_id to string for session storage
        if book_id_str in cart:
            cart[book_id_str] += 1 # Increment the quantity of the book in the cart
        else:
            cart[book_id_str] = 1 # Add the book to the cart with quantity 1
        session['cart'] = cart # Update the cart in the session

        if inventory <= 5:
            flash(f'Stock is low for this book. Only {inventory - 1} left.', 'warning')

        # Add to order history
        cur.execute("INSERT INTO orders (user_id, book_id, quantity) VALUES (%s, %s, %s)", (session['user_id'], book_id, 1)) # Insert the order into the orders table
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('cart'))

#REFERENCE https://www.youtube.com/watch?v=6WruncSoCdI - Explains adding items to the cart, managing inventory, and updating the database

@app.route('/remove_from_cart/<int:book_id>')
def remove_from_cart(book_id):
    if 'username' in session and 'cart' in session:
        cart = session['cart']
        book_id_str = str(book_id)  # Convert book_id to string to ensure compatibility with session storage
        if book_id_str in cart:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("UPDATE books SET inventory = inventory + 1 WHERE id = %s", (book_id,)) # Increase the book's inventory by 1
            mysql.connection.commit() # Commit the transaction to save changes
            if cart[book_id_str] > 1: # Check if the quantity of the book in the cart is > than 1
                cart[book_id_str] -= 1 # Decrease the quantity of the book in the cart by 1
            else:
                del cart[book_id_str]
            session['cart'] = cart
            
            # Remove from order history
            cur.execute("DELETE FROM orders WHERE user_id = %s AND book_id = %s ORDER BY order_date DESC LIMIT 1", (session['user_id'], book_id)) # Delete the order from the orders table
            mysql.connection.commit()
            cur.close()
    return redirect(url_for('cart'))

# https://github.com/01one/flask-tutorial-user-profile-template - Ive used this examples of managing session data and updating inventory in an app.

@app.route('/clear_cart')
def clear_cart():
    if 'username' in session:
        cart = session.pop('cart', {})
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        for book_id, quantity in cart.items(): # Iterate over the items in the cart (loop)
            cur.execute("UPDATE books SET inventory = inventory + %s WHERE id = %s", (quantity, book_id)) # Increase the inventory of each book by the quantity in the cart
            mysql.connection.commit()
            # Clear order history
            cur.execute("DELETE FROM orders WHERE user_id = %s AND book_id = %s", (session['user_id'], book_id)) # Delete the order from the orders table
            mysql.connection.commit()
        cur.close()
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    cart_books = [] # An empty list to store book details
    cart_quantities = {} # An empty dictionary to store book quantities
    total_price = 0
    if 'cart' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        for book_id in session['cart']:
            cur.execute("SELECT * FROM books WHERE id = %s", (int(book_id),))  # Convert book_id back to int for querying
            book = cur.fetchone()
            cart_books.append(book) # Add the book details to the list
            cart_quantities[int(book_id)] = session['cart'][book_id]  # Convert back to int for consistency
            total_price += book['price'] * session['cart'][book_id]  # Calculate total price
        cur.close()
    
    # Check user's balance
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT balance FROM tbl_users WHERE id = %s", (session['user_id'],)) # Query the user's balance
    user = cur.fetchone()
    cur.close()

    if user['balance'] < 10: # Check if the user's balance is below €10
        flash('Your balance is below €10. Please add more funds.', 'warning')
    
    return render_template('cart.html', books=cart_books, quantities=cart_quantities, total_price=total_price)

# https://roytuts.com/simple-shopping-cart-using-python-flask-mysql/ - Tells how to create a simple shopping cart in Flask, setting up routes to view the cart, add items and handle session management
# https://marketsplash.com/how-to-create-a-shopping-cart-in-flask/ - Ive used this to create a shopping cart in Flask, including routes for viewing cart contents, updating quantity, and remove items from the cart

@app.route('/admin/inventory')
def admin_inventory(): # Admin to access this page
    if 'username' in session and session['username'] == 'admin':  # Only allow admin to access this page
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM books") # Retrieve all books from the database
        books = cur.fetchall()
        cur.close()
        return render_template('admin_inventory.html', books=books) # Render the admin inventory page with the list of books
    return redirect(url_for('login'))

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST': # Check if the request method is POST (form submission)
        email = request.form['email'] # Retrieve
        name = request.form['name'] # Retrieve
        address = request.form['address'] # Retrieve
        
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("UPDATE tbl_users SET email = %s, name = %s, address = %s WHERE id = %s",  
                    (email, name, address, session['user_id']))  # Update the user's email, name, and address in the database
        mysql.connection.commit()
        cur.close()
        
        flash('Profile updated successfully', 'success')
        return redirect(url_for('user_profile'))
    
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM tbl_users WHERE id = %s", (session['user_id'],)) # Retrieve the user's details from the database
    user = cur.fetchone()
    cur.close()
    
    return render_template('edit_profile.html', user=user)

@app.route('/add_funds', methods=['GET', 'POST'])
def add_funds():
    if 'username' not in session: 
        return redirect(url_for('login'))
    
    if request.method == 'POST': 
        amount = Decimal(request.form['amount'])  # Convert to Decimal
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cur.execute("SELECT balance FROM tbl_users WHERE id = %s", (session['user_id'],)) # Retrieve the user's current balance from the database
            user = cur.fetchone()
            new_balance = Decimal(user['balance']) + amount  # Calculate the new balance, ensuring both are Decimal
            cur.execute("UPDATE tbl_users SET balance = %s WHERE id = %s", (new_balance, session['user_id'])) 
            mysql.connection.commit()
            flash('Funds added successfully', 'success')
        except Exception as e:
            flash('An error occurred: ' + str(e), 'danger')
        finally:
            cur.close()
        return redirect(url_for('user_profile'))

    return render_template('add_funds.html')

@app.route('/update_inventory/<int:book_id>', methods=['POST']) 
def update_inventory(book_id):
    if 'username' not in session or session['username'] != 'admin': # Checks if the user is logged in and is an admin
        return redirect(url_for('login'))

    new_inventory = int(request.form['new_inventory']) # Retrieve the new inventory amount from the form and convert it to an integer
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        # Fetch the current inventory
        cur.execute("SELECT inventory FROM books WHERE id = %s", (book_id,)) # Retrieve the current inventory of the book
        current_inventory = cur.fetchone()['inventory'] # Fetch the current inventory value

        # Calculate the new inventory
        updated_inventory = current_inventory + new_inventory  # Added to update the inventory by adding new stock

        # Update the inventory in the database
        cur.execute("UPDATE books SET inventory = %s WHERE id = %s", (updated_inventory, book_id)) # Update the inventory in the database
        mysql.connection.commit()
        flash('Inventory updated successfully', 'success')
    except Exception as e:
        flash('An error occurred: ' + str(e), 'danger')
    finally:
        cur.close()

    return redirect(url_for('admin_inventory')) # https://www.youtube.com/watch?v=Rxp3mkg2mRQ - This video helped in creating, reading, updating, and deleting records in Flask applications, which includes updating inventory. It demonstrates form handling and database interaction

def generate_po_number(length=10): # Helper function to generate a random PO number
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    timestamp_part = datetime.datetime.now().strftime("%Y%m%d%H%M%S") # string "%Y%m%d%H%M%S" formats a datetime object into a string, representing the year/month/day/hour/minute and second.
    return f"{random_part}-{timestamp_part}"

@app.route('/buy_book/<int:book_id>', methods=['POST'])  # Route to handle buying a book
def buy_book(book_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        # Get book details
        cur.execute("SELECT * FROM books WHERE id = %s", (book_id,)) # Retrieve the book details from the database
        book = cur.fetchone()
        if book['inventory'] < 1: #Checks if the book is out of stock
            flash('This book is out of stock.', 'danger')
            return redirect(url_for('books_page'))

        # Update book inventory
        cur.execute("UPDATE books SET inventory = inventory - 1 WHERE id = %s", (book_id,)) # Decrease the books inventory by 1
        mysql.connection.commit()

        # Generate a new PO number
        po_number = generate_po_number()
        order_date = datetime.datetime.now() # Get the current date and time

        # Insert the order into the orders table
        cur.execute("""
            INSERT INTO orders (user_id, book_id, quantity, po_number, order_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (session['user_id'], book_id, 1, po_number, order_date)) # Insert the order details into the orders table
        mysql.connection.commit()
        flash('Book purchased successfully!', 'success')
    except Exception as e:
        flash('An error occurred: ' + str(e), 'danger')
    finally:
        cur.close()

    return redirect(url_for('view_orders'))
# Reference: https://www.youtube.com/watch?v=CSHx6eCkmv0 - Helped me with managing inventory, and handling user sessions. 
# Reference: https://github.com/kaiicheng/Flask-E-Commerce-Project - Found this gold, reverse engineered and incorporated few elements.

# Function to generate a unique PO number
def generate_po_number():
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)) # Generates a random string of 10 uppercase letters and digits
    timestamp_part = datetime.datetime.now().strftime("%Y%m%d%H%M%S") # Generates a timestamp in the format YYYYMMDDHHMMSS
    return f"{random_part}-{timestamp_part}" # Combine the random string and timestamp to create a unique PO number
#REFERENCE: https://overiq.com/flask-101/creating-urls-in-flask/?utm_content=cmp-true - URL creation and handling in Flask


# Added methods=['GET', 'POST'] to allow both GET and POST requests
@app.route('/purchase', methods=['POST'])
def purchase():
    if 'username' not in session: # checks if the user is logged in
        return redirect(url_for('login'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Generate a unique PO number
    po_number = generate_po_number()
    logging.debug(f"Generated PO Number: {po_number}")

    total_cost = 0 #Initialis the Total Cost Sets total_cost to 0
    for book_id, quantity in session['cart'].items():
        # Fetch book details
        cur.execute("SELECT * FROM books WHERE id = %s", (book_id,))
        book = cur.fetchone()
        total_cost += book['price'] * quantity #Calculate the total cost of items in the cart

    # Fetch user balance
    cur.execute("SELECT balance FROM tbl_users WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()

    if user['balance'] < total_cost: # Checking if the user has sufficient funds
        flash('Insufficient funds for this purchase.', 'danger')
        cur.close() # Close the cursor if funds are insufficient
        return redirect(url_for('cart'))

    for book_id, quantity in session['cart'].items(): # Iterate over items in the cart again
        # Fetch book details
        cur.execute("SELECT * FROM books WHERE id = %s", (book_id,))
        book = cur.fetchone()

        # Insert order details
        cur.execute(
            "INSERT INTO orders (user_id, book_id, quantity, po_number, order_date) VALUES (%s, %s, %s, %s, NOW())",
            (session['user_id'], book_id, quantity, po_number)
        )
        logging.debug(f"Inserted order for book ID {book_id} with PO Number: {po_number}") # Log the order insertion

        # Update book inventory
        cur.execute("UPDATE books SET inventory = inventory - %s WHERE id = %s", (quantity, book_id)) 

    # Deduct balance
    new_balance = user['balance'] - total_cost
    cur.execute("UPDATE tbl_users SET balance = %s WHERE id = %s", (new_balance, session['user_id']))
    mysql.connection.commit() # Commit the transaction to save all changes
    cur.close()

    # Clear cart
    session.pop('cart', None)

    flash('Purchase successful!', 'success')
    return redirect(url_for('view_orders'))
# Reference: https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3 - Helped me with handling routes, and managing database transactions, which are relevant to implementing a purchase functio

# Added a route to view orders
@app.route('/view_orders')  
def view_orders():
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT o.po_number, o.order_date, b.title, o.quantity, b.price
        FROM orders o
        JOIN books b ON o.book_id = b.id
        WHERE o.user_id = %s AND o.po_number IS NOT NULL AND o.po_number != 'N/A'
        ORDER BY o.order_date DESC
    """, (session['user_id'],))
    orders = cur.fetchall()
    cur.close()

    return render_template('orders.html', orders=orders)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
