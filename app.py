"""
Connects to a SQL database using pyodbc
"""
from flask import Flask, render_template, request
import pyodbc as odbc

app = Flask(__name__)

#  Your connection details
driver_name = 'ODBC Driver 18 for SQL Server'
server_name = 'DESKTOP-310T804'
database_name = 'products'

# Create connection string
connection_string = f'DRIVER={{{driver_name}}};SERVER={server_name};DATABASE={database_name};LongAsMax=yes;Encrypt=no;Trusted_Connection=yes;'

conn = odbc.connect(connection_string)
cursor = conn.cursor()

@app.route('/')
def home():
  return render_template('index.html')

@app.route('/display')
def display_table():
  return render_template('display.html')

#   return render_template('display_table.html', table_rows=table_rows)
@app.route('/query1', methods=['POST'])
def query1():
  cursor = conn.cursor()
  cursor.execute('''
                select products.productID, cast(products.prodName as varchar) as prodName, price,
                count(orderLineItems.productID) as numberSold,
                count(orderLineItems.productID) * price as total
                from products
                left join orderLineItems on products.productID = orderLineItems.productID
                group by products.productID, cast(products.prodName as varchar), price
                order by numberSold desc
                 ''')
  result = cursor.fetchall()
    
  # Get the column names from cursor description
  columns = [column[0] for column in cursor.description]
    
  return render_template('display.html', columns=columns, result=result)

@app.route('/query2', methods=['POST'])
def query2():
  provinceID = request.form['province']
  prodName = request.form['prodName']
  cursor = conn.cursor()
  cursor.execute(f'''
                SELECT cast(people.firstname as varchar) as firstname, cast(people.lastname as varchar) as lastname
                FROM people
                JOIN orders ON people.personID = orders.personID
                JOIN orderLineItems ON orders.orderID = orderLineItems.orderID
                JOIN products ON orderLineItems.productID = products.productID
                WHERE convert(varchar, people.provinceID) = '{provinceID}' 
                and convert(varchar, products.prodName) = '{prodName}'
                 ''')
  result = cursor.fetchall()
    
  # Get the column names from cursor description
  columns = [column[0] for column in cursor.description]
    
  return render_template('display.html', columns=columns, result=result)
  
@app.route('/query3', methods=['POST'])
def query3():
  cursor = conn.cursor()
  cursor.execute('''
                  SELECT cast(people.firstname as VARCHAR) as firstname, cast(people.lastname as VARCHAR) as lastname FROM people
                  WHERE convert(varchar, people.provinceID) = 'MB'
                  EXCEPT
                  SELECT cast(people.firstname as VARCHAR), cast(people.lastname as VARCHAR) FROM people
                  JOIN orders ON people.personID = orders.personID
                  JOIN orderLineItems ON orders.orderID = orderLineItems.orderID
                  JOIN products ON orderLineItems.productID = products.productID
                  WHERE products.price > 99
                  ''')
  result = cursor.fetchall()
    
  # Get the column names from cursor description
  columns = [column[0] for column in cursor.description]
    
  return render_template('display.html', columns=columns, result=result)

@app.route('/query4', methods=['POST'])
def query4():
  cursor = conn.cursor()
  cursor.execute('''
                  SELECT DISTINCT cast(prodName as VARCHAR) as prodName
                  FROM products p
                  JOIN viewed v ON p.productID = v.productID
                  JOIN people pe ON v.personID = pe.personID
                  LEFT JOIN (
                      SELECT ioo.productID, o.personID
                      FROM orderLineItems ioo
                      JOIN orders o ON ioo.orderID = o.orderID
                  ) o ON p.productID = o.productID AND v.personID = o.personID
                  WHERE pe.provinceID = 'MB';
                  ''')
  result = cursor.fetchall()
    
  # Get the column names from cursor description
  columns = [column[0] for column in cursor.description]
    
  return render_template('display.html', columns=columns, result=result)

@app.route('/query5', methods=['POST'])
def query5():
  provinceID = request.form['province']
  cursor = conn.cursor()
  cursor.execute(f'''
                  SELECT DISTINCT cast(prodName as VARCHAR) as prodName
                  FROM products p
                  JOIN viewed v ON p.productID = v.productID
                  JOIN people pe ON v.personID = pe.personID
                  LEFT JOIN (
                      SELECT ioo.productID, o.personID
                      FROM orderLineItems ioo
                      JOIN orders o ON ioo.orderID = o.orderID
                  ) o ON p.productID = o.productID AND v.personID = o.personID
                  WHERE pe.provinceID = '{provinceID}';
                  ''')
  result = cursor.fetchall()
    
  # Get the column names from cursor description
  columns = [column[0] for column in cursor.description]
    
  return render_template('display.html', columns=columns, result=result)

if __name__ == '__main__':
  app.run(debug=True)
