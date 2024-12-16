from flask import Flask,render_template,request,redirect,session
from database import conn, cur
from functools import wraps

#functools import wraps is initialised to use the decorator function

# flask name initiates app- class obj
app = Flask(__name__)

#secret placed for runing sessions
app.secret_key="myduka123"

#Decorator function is used to give a func/route more functionality
#It runs before the route function is processed

def login_required(f):
    @wraps(f)
    def protected(*args, **kwargs):
        if 'email' in session:
            return f(*args, **kwargs)
        return redirect("/login")
    return protected




# Define a custom filter- this will be used to format the date
@app.template_filter('strftime')
def format_datetime(value, format="%B %d, %Y"):
    return value.strftime(format)





@app.route("/")
def index():
    name="Friend"
    return render_template("index.html",name=name)

@app.route("/navbar")
def navb():
    return render_template("navbar.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/about")
def about():
    return "About page info is supposed to be displayed on this route"

@app.route("/dashboard")
@login_required
def dashboardfunc():

    cur.execute("SELECT sum (p.selling_price * s.quantity) as sales, s.created_at from sales as s join products as p on p.id=s.pid GROUP BY created_at ORDER BY created_at;")
    daily_sales=cur.fetchall()
   # print(daily_sales)
    x=[]
    y=[]
    for i in daily_sales:
        x.append(i[1].strftime("%B %d, %Y"))
        y.append(float(i[0]))
        
    # list comprehension
    #lx = [i[1].strftime("%B %d, %Y") for i in daily_sales]
    #ly = [i[0] for i in daily_sales]

    #append happens because it is inside a list
    #you can also add an if statement
    #lx = [i[1].strftime("%B %d, %Y") for i in daily_sales if float(i[0])>60000]

    cur.execute("SELECT sum (p.selling_price * s.quantity) as Profit, p.name from products as p join sales as s on p.id=s.pid GROUP BY p.name ORDER BY profit desc;")
    profit_per_product=cur.fetchall()
    p=[]
    q=[]

    for z in profit_per_product:
        p.append(z[1])
        q.append(z[0])

    return render_template("dashboard.html",x=x,y=y,p=p,q=q,)


@app.route("/login", methods=["POST","GET"])
def logi():
    if request.method=="POST":
        email=request.form["mail"]
        password=request.form["passw"]
        cur.execute("select id from users where email='{}' and password='{}'".format(email,password))
        row= cur.fetchone()
        if row== None:
            return "Invalid Credentials"
        else:
            session["email"]= email
            return redirect("/dashboard")
    else:
        return render_template("login.html")
    

@app.route("/register", methods=["GET","POST"])
def reg():
    if request.method=="GET":
         return render_template("register.html")
    else:
        name=request.form["jina"]
        email=request.form["mail"]
        password=request.form["passw"]
        query_reg ="insert into users(name,email,password) values('{}','{}','{}')".format(name,email,password)
        cur.execute(query_reg)
        conn.commit()
        return redirect("/dashboard")




@app.route("/products", methods=["GET", "POST"])
#get is fetching from database and post is getting from form which is filled and posted
#model view controller uses this to get data from database and send it to view-which works across all frameworks
@login_required
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
        #print(name, buying_price, selling_price, stock_quantity) 
        if selling_price < buying_price:
            return "Selling price should be greater than buying price"
        
        query="insert into products(name,buying_price,selling_price,stock_quantity) "\
        "values('{}',{},{},{})".format(name,buying_price,selling_price,stock_quantity)

        cur.execute(query)
        conn.commit()
        return redirect("/products")
        
        
    

@app.route("/sales",methods=["GET", "POST"])
@login_required
def salez():
    if request.method=="POST":
        pid=request.form["pid"]
        amount=request.form["amount"]
        #print(pid,amount)
        query_s="insert into sales(pid,quantity,created_at) "\
        "values('{}',{},{})".format(pid,amount,'now()')
        cur.execute(query_s)
        conn.commit()
        return redirect("/sales")
    else:
        cur.execute("select * from products")
        products=cur.fetchall()
        cur.execute("select sales.ID, products.Name, sales.quantity, sales.created_at "\
                    "from sales inner join products on sales.pid = products.id")
        sales=cur.fetchall()
        return render_template("sales.html",products=products,sales=sales)
    

app.run(debug=True)