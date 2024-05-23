from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL, MySQLdb
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = 'supersecretkey'

# MySQL Configuration
app.config["MYSQL_HOST"] = "10.0.0.4"  # my VM IP
app.config["MYSQL_USER"] = "remote_user"
app.config["MYSQL_PASSWORD"] = "alexander"
app.config["MYSQL_DB"] = "bookstore_users"

mysql = MySQL(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':  # Corrected here
        username = request.form['username']
        pwd = request.form['password']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cur.execute("SELECT * FROM tbl_users WHERE username = %s", (username,))
            user = cur.fetchone()
        except Exception as e:
            cur.close()
            return render_template("login.html", error="An error occurred: " + str(e))
        cur.close()
        if user and pwd == user['password']:
            session["username"] = user['username']
            session["user_id"] = user['id']
            return redirect(url_for("profile"))
        else:
            return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        email = request.form['email']
        name = request.form['name']
        address = request.form['address']
        
        if not username or not pwd or not email or not name or not address:
            flash('All fields are required!', 'danger')
            return redirect(url_for('register'))
        
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cur.execute("INSERT INTO tbl_users (username, password, email, name, address) VALUES (%s, %s, %s, %s, %s)", 
                        (username, pwd, email, name, address))
            mysql.connection.commit()
        except Exception as e:
            cur.close()
            return render_template("register.html", error="An error occurred: " + str(e))
        cur.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM tbl_users WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    cur.close()
    
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT o.*, b.title FROM orders o JOIN books b ON o.book_id = b.id WHERE o.user_id = %s", (session['user_id'],))
    orders = cur.fetchall()
    cur.close()
    
    return render_template('profile.html', user=user, orders=orders)

@app.route('/books')
def books_page():
    query = request.args.get('query')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if query:
        cur.execute("SELECT * FROM books WHERE title LIKE %s", ('%' + query + '%',))
    else:
        cur.execute("SELECT * FROM books")
    books = cur.fetchall()
    cur.close()
    
    for book in books:
        if book['inventory'] < 5:
            flash(f"Low stock alert: Only {book['inventory']} left of '{book['title']}'", 'warning')
    
    return render_template('books.html', books=books)

@app.route('/add_to_cart/<int:book_id>')
def add_to_cart(book_id):
    if 'username' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT inventory FROM books WHERE id = %s", (book_id,))
        inventory = cur.fetchone()['inventory']
        if inventory < 1:
            flash('This book is out of stock.', 'danger')
            return redirect(url_for('books_page'))
        cur.execute("UPDATE books SET inventory = inventory - 1 WHERE id = %s", (book_id,))
        mysql.connection.commit()
        
        if 'cart' not in session:
            session['cart'] = {}
        cart = session['cart']
        book_id_str = str(book_id)  # Convert book_id to string to ensure compatibility with session storage
        if book_id_str in cart:
            cart[book_id_str] += 1
        else:
            cart[book_id_str] = 1
        session['cart'] = cart
        
        if inventory <= 5:
            flash(f'Stock is low for this book. Only {inventory - 1} left.', 'warning')
        
        # Add to order history
        cur.execute("INSERT INTO orders (user_id, book_id, quantity) VALUES (%s, %s, %s)", (session['user_id'], book_id, 1))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:book_id>')
def remove_from_cart(book_id):
    if 'username' in session and 'cart' in session:
        cart = session['cart']
        book_id_str = str(book_id)  # Convert book_id to string to ensure compatibility with session storage
        if book_id_str in cart:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("UPDATE books SET inventory = inventory + 1 WHERE id = %s", (book_id,))
            mysql.connection.commit()
            if cart[book_id_str] > 1:
                cart[book_id_str] -= 1
            else:
                del cart[book_id_str]
            session['cart'] = cart
            
            # Remove from order history
            cur.execute("DELETE FROM orders WHERE user_id = %s AND book_id = %s ORDER BY order_date DESC LIMIT 1", (session['user_id'], book_id))
            mysql.connection.commit()
            cur.close()
    return redirect(url_for('cart'))

@app.route('/clear_cart')
def clear_cart():
    if 'username' in session:
        cart = session.pop('cart', {})
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        for book_id, quantity in cart.items():
            cur.execute("UPDATE books SET inventory = inventory + %s WHERE id = %s", (quantity, book_id))
            mysql.connection.commit()
            # Clear order history
            cur.execute("DELETE FROM orders WHERE user_id = %s AND book_id = %s", (session['user_id'], book_id))
            mysql.connection.commit()
        cur.close()
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    cart_books = []
    cart_quantities = {}
    total_price = 0
    if 'cart' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        for book_id in session['cart']:
            cur.execute("SELECT * FROM books WHERE id = %s", (int(book_id),))  # Convert book_id back to int for querying
            book = cur.fetchone()
            cart_books.append(book)
            cart_quantities[int(book_id)] = session['cart'][book_id]  # Convert back to int for consistency
            total_price += book['price'] * session['cart'][book_id]  # Calculate total price
        cur.close()
    
    return render_template('cart.html', books=cart_books, quantities=cart_quantities, total_price=total_price)

@app.route('/admin/inventory')
def admin_inventory():
    if 'username' in session and session['username'] == 'admin':  # Only allow admin to access this page
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM books")
        books = cur.fetchall()
        cur.close()
        return render_template('admin_inventory.html', books=books)
    return redirect(url_for('login'))

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        address = request.form['address']
        
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("UPDATE tbl_users SET email = %s, name = %s, address = %s WHERE id = %s", 
                    (email, name, address, session['user_id']))
        mysql.connection.commit()
        cur.close()
        
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM tbl_users WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    cur.close()
    
    return render_template('edit_profile.html', user=user)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
