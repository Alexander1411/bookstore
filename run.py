from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'supersecretkey'

books = [
    {"id": 1, "title": "The Body Keeps the Score: Brain, Mind, and Body in the Healing of Trauma", "author": "Bessel van der Kolk", "price": 12.38},
    {"id": 2, "title": "The Myth of Normal: Illness, Health & Healing in a Toxic Culture", "author": "Gabor Maté with Daniel Maté", "price": 6.42},
    {"id": 3, "title": "Scattered Minds: The Origins and Healing of Attention Deficit Disorder", "author": "Dr. Gabor Maté", "price": 11.68},
    {"id": 4, "title": "ADHD 2.0: New Science and Essential Strategies for Thriving with Distraction", "author": "Edward M. Hallowell, John J. Ratey", "price": 11.68},
    {"id": 5, "title": "Grit: Why Passion and Resilience are the Secrets to Success", "author": "Angela Duckworth", "price": 11.68},
    {"id": 6, "title": "Quit: The Power of Knowing When to Walk Away", "author": "Annie Duke", "price": 11.49}
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
