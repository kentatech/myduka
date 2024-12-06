from flask import Flask,render_template,request,redirect
from database import conn, cur

# flask name initiates app
app = Flask(__name__)

# Define a custom filter- this will be used to format the date(should be done after importing datetime)
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

@app.route("/products", methods=["GET", "POST"])
#get is fetching from database and post is getting from form which is filled and posted
#model view controller uses this to get data from database and send it to view-which works across all frameworks
def products():
    if request.method == "GET":
        cur.execute("SELECT * FROM products order by id desc")
        products = cur.fetchall()
        print(products)
        return render_template("products.html", products=products)
    else:
        name = request.form["name"]
        buying_price = float(request.form["bp"])
        selling_price = float(request.form["sp"])
        stock_quantity = int(request.form["stqu"])
        print(name, buying_price, selling_price, stock_quantity) 
        if selling_price < buying_price:
            return "Selling price should be greater than buying price"
        query="insert into products(name,buying_price,selling_price,stock_quantity) "\
        "values('{}',{},{},{})".format(name,buying_price,selling_price,stock_quantity)
        cur.execute(query)
        conn.commit()
        return redirect("/products")
        
        
    

@app.route("/sales")
def salez():
    cur.execute("select sales.ID, products.Name, sales.quantity, sales.created_at from sales inner join products on sales.pid = products.id")
    return render_template("sales.html",sales=cur.fetchall(),products=cur.fetchall())

app.run(debug=True)