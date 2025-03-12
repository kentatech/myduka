from flask import Flask,render_template,request,redirect,session,flash
from database import conn, cur
from functools import wraps
from flask_bcrypt import Bcrypt

#functools import wraps is initialised to use the decorator function

# flask name initiates app- class obj
app = Flask(__name__)
bcrypt = Bcrypt(app)
#secret placed for runing sessions
app.secret_key = b'!mydUIOkaknknkn9923!'

#Decorator function is used to give a func/route more functionality
#It runs before the route function is processed to see if user is logged in

def login_required(f):
    @wraps(f)
    def protected(*args, **kwargs):
        if 'email' in session:
            return f(*args, **kwargs)
        return redirect(f"/login?next={request.path}")
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
    flash("You have successfully Logged out!")
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

    cur.execute("""
    WITH daily_sales AS (
        SELECT 
            SUM ((p.selling_price - p.buying_price) * s.quantity) AS sales, 
            s.created_at::DATE AS sale_date
        FROM 
            sales AS s
        JOIN 
            products AS p 
        ON 
            p.id = s.pid
        GROUP BY 
            s.created_at::DATE
    ),
    daily_expenses AS (
        SELECT 
            SUM(amount) AS total_expenses, 
            purchase_date::DATE AS expense_date
        FROM 
            purchases
        GROUP BY 
            purchase_date::DATE
    )
    SELECT 
        s.sale_date AS profit_date,
        COALESCE(s.sales, 0) - COALESCE(e.total_expenses, 0) AS final_profit
    FROM 
        daily_sales AS s
    FULL OUTER JOIN 
        daily_expenses AS e
    ON 
        s.sale_date = e.expense_date
    WHERE
        s.sale_date = '2025-03-07' OR e.expense_date = '2025-03-07'
    """)
    
    final_profit = cur.fetchone()
    print(final_profit)

    # a=[]
    # b=[]
    # for c in final_profit:
    #     a.append(c[0])
    #     b.append(float(c[1]))
    
    return render_template("dashboard.html",x=x,y=y,p=p,q=q)


@app.route("/login", methods=["POST","GET"])
def login():
    if request.method=="POST":
        email=request.form["mail"]
        password=request.form["passw"]

        #check password match between hashed password and input password
        relationship = "select password from users where email='{}'".format(email)
        cur.execute(relationship)
        result = cur.fetchone()
        print("----------------------",result[0])
        hw_pw = result[0]
        pass_bool = bcrypt.check_password_hash(hw_pw, password)
        if not pass_bool:
            return "Invalid Password!!!!"    
        else:
            #check if email & password Co-exists in the same row
            # cur.execute("select id from users where email='{}' and password='{}'".format(email,password))
            # row = cur.fetchone()
            # if row is None:
            #     return "Invalid Email or Password"
            # else:
                session["email"] = email
                redirect_url = request.form.get("next", "/dashboard") 
                # print("Redirecting to:", redirect_url) #debug print
                return redirect(redirect_url)
    else:
        next_page= request.args.get("next", "/dashboard")
        # print(f"Next page from query string: {next_page}")  # Debug print
        return render_template("login.html", next=next_page)
    

@app.route("/register", methods=["GET","POST"])
def reg():
    if request.method=="GET":
         return render_template("register.html")
    else:
        name=request.form["jina"]
        email=request.form["mail"]
        password=request.form["passw"]
        #check if email exists
        cur.execute("select id from users where email='{}'".format(email))
        row=cur.fetchone()
        if row is not None:
            return "User with that email already exists"        
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            # check if password is hashed
            print(f"HASHED PASSWORD IS...." + hashed_password)
            query_reg ="insert into users(name,email,password) values('{}','{}','{}')".format(name,email,hashed_password)
            cur.execute(query_reg)
            conn.commit()
            return redirect("/login")
        


@app.route("/products", methods = ["GET", "POST"])
#get is fetching from database and post is getting from form which is filled and posted
#model view controller uses this to get data from database and send it to view-which works across all frameworks
@login_required
def products():

    if request.method == "GET":
        cur.execute("SELECT * FROM products order by id desc")
        products = cur.fetchall()
        # print(products)
        return render_template("products.html", products=products)
    else:
        name = request.form["name"]
        buying_price = float(request.form["bp"])
        selling_price = float(request.form["sp"])
        stock_quantity = int(request.form["stqu"])
        # print(name, buying_price, selling_price, stock_quantity) 
            
        if selling_price < buying_price:
            return "Selling price should be greater than buying price"
        
        query ="insert into products(name,buying_price,selling_price,stock_quantity) "\
        "values('{}',{},{},{})".format(name,buying_price,selling_price,stock_quantity)

        cur.execute(query)
        conn.commit()
        return redirect("/products")
     
@app.route("/sales",methods = ["GET", "POST"])
@login_required
def salez():
    if request.method =="POST":
        pid=request.form["pid"]
        amount=int(request.form["amount"])
        #print(pid,amount)

        # Validate the input
        if amount is None:
            return "Please enter the sale amount"
        if amount <= 0:
            return "Sale amount should be greater than zero"

        # Check the current stock quantity
        cur.execute("SELECT stock_quantity FROM products WHERE id = {}".format(pid,))
        q = cur.fetchone()
        current_quantity = q[0]        
        if current_quantity == 0:
            return "Good out of stock" 
        if amount > current_quantity:
            return "Sale amount exceeds available stock"
        
        # insert after input has validated quantity
        query_s="insert into sales(pid,quantity,created_at) "\
        "values('{}',{},now())".format(pid,amount)
        cur.execute(query_s)
        conn.commit()

        # Update the products table to decrement the product count
        query_u = "UPDATE products SET stock_quantity = stock_quantity - {} WHERE id = {}".format(amount, pid)
        cur.execute(query_u)

        return redirect("/sales")
    
    else:
        cur.execute("select * from products")
        products=cur.fetchall()
        cur.execute("select sales.ID, products.Name, sales.quantity, sales.created_at "\
                    "from sales inner join products on sales.pid = products.id")
        sales=cur.fetchall()
        
        return render_template("sales.html",products=products,sales=sales)
        
@app.route("/purchases", methods=["GET", "POST"])
@login_required
def expenses():
    if request.method=="GET":
        cur.execute("SELECT * FROM PURCHASES ORDER BY purchase_date DESC")
        expenses=cur.fetchall()
        return render_template("expenses.html", expenses=expenses)
    else:
        expense_category = request.form["expense_category"] 
        description = request.form["description"]
        amount = int(request.form["amount"]) 

        query_create_expense="INSERT INTO purchases(expense_category, description, amount, purchase_date)"\
                        "VALUES('{}','{}',{}, now())".format(expense_category,description,amount)
        cur.execute(query_create_expense)
        conn.commit()
        return redirect("/purchases")
   
@app.route("/stock", methods=["GET", "POST"])
@login_required
def stock():
    if request.method=="GET":
        cur.execute("SELECT stock.stock_id, products.name, stock.quantity, stock.stock_in_date FROM stock join products on products.id=stock.pid")
        stock=cur.fetchall()
        cur.execute("SELECT * FROM products ORDER BY name ASC")
        products=cur.fetchall()
        return render_template("stock.html", stock=stock, products=products)
    else:
        pid=request.form["pid"]
        quantity=request.form["quantity"]
        query_update_stock="INSERT INTO stock(quantity, pid,stock_in_date)"\
                            "VALUES({},{},now())".format(quantity,pid)
        cur.execute(query_update_stock)
        conn.commit()
        return redirect("/stock")


@app.route("/base")
def base():
    return "thankyou"
    render_template("base.html")

@app.route("/update-products", methods=["GET","POST"])
def update_product():
    name=request.form["name"]
    buying_price=float(request.form["bp"])
    selling_price=float(request.form["sp"])
    stock_quantity=int(request.form["stqu"])
    id=request.form["id"]    
    query="update products set name='{}',buying_price={},selling_price={},stock_quantity={} where id={}".format(name,buying_price,selling_price,stock_quantity,id)
    cur.execute(query)
    conn.commit()   
    return redirect("/products")
    
    
if __name__ == '__main__':
    app.run(debug=True)






