from flask import Flask, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    # Add login logic here
    session['user'] = 'user'
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    # Add logout logic here
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/books')
def books():
    # Add logic to show books
    return render_template('books.html')

@app.route('/cart')
def cart():
    # Add logic to show cart
    return render_template('cart.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
