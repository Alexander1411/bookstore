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
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cur.execute("SELECT username, password FROM tbl_users WHERE username = %s", (username,))
            user = cur.fetchone()
        except Exception as e:
            cur.close()
            return render_template("login.html", error="An error occurred: " + str(e))
        cur.close()
        if user and pwd == user['password']:
            session["username"] = user['username']
            return redirect(url_for("books_page"))
        else:
            return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cur.execute("INSERT INTO tbl_users (username, password) VALUES (%s, %s)", (username, pwd))
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
    return redirect(url_for('home'))

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
        cur.close()
        
        if 'cart' not in session:
            session['cart'] = {}
        cart = session['cart']
        if book_id in cart:
            cart[book_id] += 1
        else:
            cart[book_id] = 1
        session['cart'] = cart
        
        if inventory <= 5:
            flash(f'Stock is low for this book. Only {inventory - 1} left.', 'warning')
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:book_id>')
def remove_from_cart(book_id):
    if 'username' in session and 'cart' in session:
        cart = session['cart']
        if book_id in cart:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("UPDATE books SET inventory = inventory + 1 WHERE id = %s", (book_id,))
            mysql.connection.commit()
            cur.close()
            if cart[book_id] > 1:
                cart[book_id] -= 1
            else:
                del cart[book_id]
        session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/clear_cart')
def clear_cart():
    if 'username' in session:
        cart = session.pop('cart', {})
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        for book_id, quantity in cart.items():
            cur.execute("UPDATE books SET inventory = inventory + %s WHERE id = %s", (quantity, book_id))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    if 'username' not in session:
        return redirect(url_for('login'))
    cart_books = []
    cart_quantities = {}
    if 'cart' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        for book_id in session['cart']:
            cur.execute("SELECT * FROM books WHERE id = %s", (book_id,))
            book = cur.fetchone()
            cart_books.append(book)
            cart_quantities[book_id] = session['cart'][book_id]
        cur.close()
    return render_template('cart.html', books=cart_books, quantities=cart_quantities)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
