from flask import Flask

app = Flask(__main__)

@app.route("/")
def hello():
    return ("Hello! Main page")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8080') # indent this line