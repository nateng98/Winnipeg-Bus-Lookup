"""
Connects to a SQL database using pyodbc
"""
from flask import Flask, render_template
import pyodbc as odbc

app = Flask(__name__)

#  Your connection details
driver_name = 'SQL SERVER'
server_name = 'DESKTOP-310T804'
database_name = 'products'

# Create connection string
connection_string = f'DRIVER={{{driver_name}}};SERVER={server_name};DATABASE={database_name};TrustServerCertificate=yes'

@app.route('/')
def home():
  return render_template('index.html')

@app.route('/display_table')
def display_table():
  
  conn = odbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=DESKTOP-310T804;DATABASE=products;LongAsMax=yes;Encrypt=no;Trusted_Connection=yes;')
  cursor = conn.cursor()

  cursor.execute("SELECT * FROM people")
  table_rows = cursor.fetchall()

  cursor.close()
  conn.close()

  return render_template('display_table.html', table_rows=table_rows)

if __name__ == '__main__':
  app.run(debug=True)
