# Winnipeg-Bus-Lookup

Making use of Python and SQL, this project establishes a comprehensive database for accessing Winnipeg bus schedules and weather information in the past, offering valuable insights into the impact of weather on public transportation efficiency in Winnipeg.

[Demo Video](https://youtu.be/MitG2gKu_SI)

## Requirements (for Linux)

- Python 3.
- Flask
- pymssql

*(Already been installed on Aviary)*

## Configuration

Edit the `config.ini` file

```
; ==== URANIUM ====
Server = uranium.cs.umanitoba.ca
User = [username]
Password = [password]
Database = cs3380
```

* Note: In any case that require you to run the web application on your local machine, comment URANIUM section and uncomment LOCALHOST section in both `app.py` and `config.ini`

Edit `app.py`
```py
# | uncomment this line
# ▼
# import pyodbc as odbc

# | comment this line
# ▼
import pymssql as mssql
```
```py
# | uncomment this section
# ▼
# # LOCALHOST - Access values from the configuration file (config.ini)
# driver_name = config.get('Database', 'Driver')
# server_name = config.get('Database', 'Server')
# database_name = config.get('Database', 'Database')
# encrypt = config.get('Database', 'Encrypt')
# trusted_connection = config.get('Database', 'Trusted_Connection')

# # This is the connection string for pyodbc
# connection_string = (
#   f'DRIVER={{{driver_name}}};'
#   f'SERVER={server_name};'
#   f'DATABASE={database_name};'
#   f'Encrypt={encrypt};'
#   f'Trusted_Connection={trusted_connection};'
# )
# conn = odbc.connect(connection_string)

# | comment this section
# ▼
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
```

Edit `config.ini`
```
; | uncomment this section
; ▼
; ==== LOCALHOST (Windows) ====
; Driver = ODBC Driver 18 for SQL Server ;(if the most recent driver is installed)
; Server = [localhost server]
; Database = cc3380
; Encrypt = no
; Trusted_Connection = yes

; | comment this section
; ▼
; ==== URANIUM ====
Server = uranium.cs.umanitoba.ca
User = [username]
Password = [password]
Database = cs3380
```

## How to run

1. `cd Winnipeg-Bus-Lookup`
2. Run python app `python3 app.py`
3. Open in browser `http://[random_name].cs.umanitoba.ca:5000`

Example output on console
```bash
[nguyen74@crow Winnipeg-Bus-Lookup]> python3 app.py
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://crow.cs.umanitoba.ca:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 108-967-247
```

## Authors

- [Emily Bond]()
- [Nhat Anh Nguyen](https://github.com/nateng98)
