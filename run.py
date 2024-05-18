from flask import Flask

app = Flask(__main__)

@app.route("/")
def home():
    return "Hello! Main page <h1>HELLO<h1>1"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8080') # indent this line