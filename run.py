from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'your_username'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'bookstore'

mysql = MySQL(app)

books = [
    {"id": 1, "title": "The Body Keeps the Score: Brain, Mind, and Body in the Healing of Trauma", "author": "Bessel van der Kolk", "price": 12.38, "image_url": "/static/static/images/the-body-keeps-the-score.jpg"},
    {"id": 2, "title": "The Myth of Normal: Illness, Health & Healing in a Toxic Culture", "author": "Gabor Maté with Daniel Maté", "price": 6.42, "image_url": "/static/static/images/the-myth-of-normal.jpg"},
    {"id": 3, "title": "Scattered Minds: The Origins and Healing of Attention Deficit Disorder", "author": "Dr. Gabor Maté", "price": 11.68, "image_url": "/static/static/images/scattered-minds.jpg"},
    {"id": 4, "title": "ADHD 2.0: New Science and Essential Strategies for Thriving with Distraction", "author": "Edward M. Hallowell, John J. Ratey", "price": 11.68, "image_url": "/static/static/images/adhd-2.jpg"},
    {"id": 5, "title": "Grit: Why Passion and Resilience are the Secrets to Success", "author": "Angela Duckworth", "price": 11.68, "image_url": "/static/static/images/grit.jpg"},
    {"id": 6, "title": "Quit: The Power of Knowing When to Walk Away", "author": "Annie Duke", "price": 11.49, "image_url": "/static/static/images/quit.jpg"}
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    session['user'] = 'user'
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/books')
def books_page():
    query = request.args.get('query')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if query:
        cursor.execute("SELECT * FROM books WHERE title LIKE %s", ('%' + query + '%',))
    else:
        cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    return render_template('books.html', books=books)

@app.route('/add_to_cart/<int:book_id>')
def add_to_cart(book_id):
    if 'user' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO cart (user_id, book_id) VALUES (%s, %s)", (session['user'], book_id))
        mysql.connection.commit()
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:book_id>')
def remove_from_cart(book_id):
    if 'user' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("DELETE FROM cart WHERE user_id = %s AND book_id = %s", (session['user'], book_id))
        mysql.connection.commit()
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    if 'user' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT books.* FROM books INNER JOIN cart ON books.id = cart.book_id WHERE cart.user_id = %s", (session['user'],))
        cart_books = cursor.fetchall()
        return render_template('cart.html', books=cart_books)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
