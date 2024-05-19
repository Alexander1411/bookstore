from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = 'supersecretkey'

# MySQL Configuration
app.config["MYSQL_HOST"] = "10.0.0.4" #my vm ip
app.config["MYSQL_USER"] = "remote_user"
app.config["MYSQL_PASSWORD"] = "yourpassword"
app.config["MYSQL_DB"] = "bookstore_users"


mysql = MySQL(app)

# Sample books data
books = [
    {"id": 1, "title": "The Body Keeps the Score: Brain, Mind, and Body in the Healing of Trauma", "author": "Bessel van der Kolk", "price": 12.38, "image_url": "/static/static/images/the-body-keeps-the-score.jpg"},
    {"id": 2, "title": "The Myth of Normal: Illness, Health & Healing in a Toxic Culture", "author": "Gabor Maté with Daniel Maté", "price": 6.42, "image_url": "/static/static/images/the-myth-of-normal.jpg"},
    {"id": 3, "title": "Scattered Minds: The Origins and Healing of Attention Deficit Disorder", "author": "Dr. Gabor Maté", "price": 11.68, "image_url": "/static/static/images/scattered-minds.jpg"},
    {"id": 4, "title": "ADHD 2.0: New Science and Essential Strategies for Thriving with Distraction", "author": "Edward M. Hallowell, John J. Ratey", "price": 11.68, "image_url": "/static/static/images/adhd-2.jpg"},
    {"id": 5, "title": "Grit: Why Passion and Resilience are the Secrets to Success", "author": "Angela Duckworth", "price": 11.68, "image_url": "/static/static/images/grit.jpg"},
    {"id": 6, "title": "Quit: The Power of Knowing When to Walk Away", "author": "Annie Duke", "price": 11.49, "image_url": "/static/static/images/quit.jpg"}
]

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT username, password FROM tbl_users WHERE username = %s", (username,))
            user = cur.fetchone()
        except Exception as e:
            cur.close()
            return render_template("login.html", error="An error occurred: " + str(e))
        cur.close()
        if user and pwd == user[1]:
            session["username"] = user[0]
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        cur = mysql.connection.cursor()
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
    if query:
        filtered_books = [book for book in books if query.lower() in book['title'].lower()]
    else:
        filtered_books = books
    return render_template('books.html', books=filtered_books)

@app.route('/add_to_cart/<int:book_id>')
def add_to_cart(book_id):
    if 'username' in session:
        if 'cart' not in session:
            session['cart'] = {}
        cart = session['cart']
        if book_id in cart:
            cart[book_id] += 1
        else:
            cart[book_id] = 1
        session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:book_id>')
def remove_from_cart(book_id):
    if 'username' in session and 'cart' in session:
        cart = session['cart']
        if book_id in cart:
            if cart[book_id] > 1:
                cart[book_id] -= 1
            else:
                del cart[book_id]
        session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/clear_cart')
def clear_cart():
    if 'username' in session:
        session.pop('cart', None)
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart_books = [book for book in books if book['id'] in session.get('cart', {})]
    cart_quantities = {book_id: session['cart'][book_id] for book_id in session.get('cart', {})}
    return render_template('cart.html', books=cart_books, quantities=cart_quantities)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
