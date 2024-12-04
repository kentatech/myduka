from flask import Flask,render_template
from database import conn, cur

app = Flask(__name__)



@app.route("/")
def index():
    name="Dev-Joe"
    return render_template("index.html",myname=name)

@app.route("/about")
def about():
    return "About page info is supposed to be displayed on this route"

@app.route("/products")
def prods():
    cur.execute("select * from products")
    return render_template("products.html",products=cur.fetchall())



app.run()