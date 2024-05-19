from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'supersecretkey'

books = [
    {"id": 1, "title": "Book One", "author": "Author One"},
    {"id": 2, "title": "Book Two", "author": "Author Two"},
    {"id": 3, "title": "Book Three", "author": "Author Three"},
    {"id": 4, "title": "Book Four", "author": "Author Four"},
    {"id": 5, "title": "Book Five", "author": "Author Five"},
    {"id": 6, "title": "Book Six", "author": "Author Six"}
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
    if query:
        filtered_books = [book for book in books if query.lower() in book['title'].lower()]
    else:
        filtered_books = books
    return render_template('books.html', books=filtered_books)

@app.route('/cart')
def cart():
    return render_template('cart.html')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
