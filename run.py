from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def hello():
    return "<h1>Hello World but bigger</h1>"

@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/shop")
def shop():
    return render_template("shop.html")

@app.route("/search")
def search():
    query = request.args.get('query')
    return f"Search results for: {query}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
