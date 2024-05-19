from flask import Flask

app = Flask(__name__)

@app.route("/")#URL leading to method
def hello(): # Name of the method
 return "<h1>Hello World but bigger</h1>!" #indent this line

@app.route("/about/<username>")
def about_page(username):
    return f"<h1>This is about page of {username}</h1>"
 
if __name__ == "__main__":
 app.run(host='0.0.0.0', port='8080') # indent this line