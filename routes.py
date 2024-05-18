from flask import render_template
from bookstore import app

@app.route("/about")
def about():
    return render_template('about.html')
