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

# @app.route('/display_table')
# def display_table():


#   cursor.execute("SELECT * FROM people")
#   table_rows = cursor.fetchall()

#   cursor.close()
#   conn.close()

#   return render_template('display_table.html', table_rows=table_rows)
@app.route('/query1', methods=['POST'])
def query1():
  cursor = conn.cursor()
  cursor.execute('SELECT * FROM People INNER JOIN Orders ON People.personID = Orders.personID')
  result = cursor.fetchall()
    
  # Get the column names from cursor description
  columns = [column[0] for column in cursor.description]
    
  return render_template('index.html', columns=columns, result=result)

@app.route('/query2', methods=['POST'])
def query2():
  cursor = conn.cursor()
  cursor.execute('SELECT prodName FROM Products as p LEFT JOIN viewed as v on v.productID=p.productID LEFT JOIN orderLineItems as o ON o.productID=p.productID WHERE o.orderID is NULL and v.productID is NULL')
  result = cursor.fetchall()
    
  # Get the column names from cursor description
  columns = [column[0] for column in cursor.description]
    
  return render_template('index.html', columns=columns, result=result)
  
@app.route('/query3', methods=['POST'])
def query3():
  cursor = conn.cursor()
  cursor.execute('''
                    SELECT cast(people.firstname as VARCHAR) as firstname, cast(people.lastname as VARCHAR) as lastname FROM people
                    WHERE people.provinceID = 'MB'
                    EXCEPT
                    SELECT cast(people.firstname as VARCHAR), cast(people.lastname as VARCHAR) FROM people
                    INNER JOIN orders ON people.personID = orders.personID
                    INNER JOIN orderLineItems ON orders.orderID = orderLineItems.orderID
                    INNER JOIN products ON orderLineItems.productID = products.productID
                    WHERE products.price > 99
                   ''')
  result = cursor.fetchall()
    
  # Get the column names from cursor description
  columns = [column[0] for column in cursor.description]
    
  return render_template('index.html', columns=columns, result=result)

@app.route('/query4', methods=['POST'])
def query4():
  cursor = conn.cursor()
  cursor.execute('''
                  SELECT DISTINCT cast(prodName as VARCHAR) as prodName
                  FROM products p
                  INNER JOIN viewed v ON p.productID = v.productID
                  INNER JOIN people pe ON v.personID = pe.personID
                  LEFT JOIN (
                      SELECT ioo.productID, o.personID
                      FROM orderLineItems ioo
                      INNER JOIN orders o ON ioo.orderID = o.orderID
                  ) o ON p.productID = o.productID AND v.personID = o.personID
                  WHERE pe.provinceID = 'MB';
                   ''')
  result = cursor.fetchall()
    
  # Get the column names from cursor description
  columns = [column[0] for column in cursor.description]
    
  return render_template('index.html', columns=columns, result=result)

if __name__ == '__main__':
  app.run(debug=True)
