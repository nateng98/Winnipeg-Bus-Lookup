"""
Connects to a SQL database using pymssql
"""
import configparser
from flask import Flask, render_template, request

# import pyodbc as odbc
import pymssql as mssql

app = Flask(__name__)

def read_config(file_path):
  config = configparser.ConfigParser()
  config.read(file_path)
  return config

config_file = 'config.ini'
config = read_config(config_file)

# LOCALHOST - Access values from the configuration file (config.ini)
# driver_name = config.get('Database', 'Driver')
# server_name = config.get('Database', 'Server')
# database_name = config.get('Database', 'Database')
# encrypt = config.get('Database', 'Encrypt')
# trusted_connection = config.get('Database', 'Trusted_Connection')

# This is the connection string for pyodbc
# connection_string = (
#   f'DRIVER={{{driver_name}}};'
#   f'SERVER={server_name};'
#   f'DATABASE={database_name};'
#   f'Encrypt={encrypt};'
#   f'Trusted_Connection={trusted_connection};'
# )
# conn = odbc.connect(connection_string)


# URANIUM - Access values from the configuration file (config.ini)
server_name = config.get('Database', 'Server')
user = config.get('Database', 'User')
password = config.get('Database', 'Password')
database_name = config.get('Database', 'Database')

conn = mssql.connect(
  server=server_name,
  user=user,
  password=password,
  database=database_name
)

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
