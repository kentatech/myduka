from flask import Flask,render_template
from database import conn, cur

app = Flask(__name__)



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return "About page info is supposed to be displayed on this route"

@app.route("/products")
def productspage():
    cur.execute ("select * from products")
    products=cur.fetchall()
    for x in products:
        print(x)
    

app.run()