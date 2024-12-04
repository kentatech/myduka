from flask import Flask,render_template
from database import conn, cur
from datetime import datetime

app = Flask(__name__)

# Define a custom filter
@app.template_filter('strftime')
def format_datetime(value, format="%B %d, %Y"):
    return value.strftime(format)

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

@app.route("/sales")
def salez():
    cur.execute("select sales.ID, products.Name, sales.quantity, sales.created_at from sales inner join products on sales.pid = products.id")
    return render_template("sales.html",sales=cur.fetchall(),products=cur.fetchall())

app.run(debug=True)