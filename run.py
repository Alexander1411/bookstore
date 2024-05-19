from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")#URL leading to method
def hello(): # Name of the method
 return "<h1>Hello World but bigger</h1>!" #indent this line

@app.route("/")
@app.route('/home')
def home():
    return render_template(home.html)
 
if __name__ == "__main__":
 app.run(host='0.0.0.0', port='8080') # indent this line