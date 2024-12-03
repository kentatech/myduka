from database import conn, cur


def fectchProducts():
    cur.execute ("select * from products")
    products=cur.fetchall()
    for x in products:
        print(x)
fectchProducts()