from flask import Flask, render_template, request
import pyodbc

app = Flask(__name__)

#  Your connection details
server_name = 'your_server_name'
database_name = 'your_database_name'
username = 'your_username'
password = 'your_password'

# Create connection string
connection_string = f'DRIVER={{SQL Server}};' \
                    f'SERVER={server_name};' \
                    f'DATABASE={database_name}'; \
                    f'UID={username}'; \
                    f'PWD={password}'

@app.route('/', methods=['GET','POST'])
def index():
  combinedStr = None
  
  if request.method == 'POST':
    userInput = request.form['user_input']
    if len(userInput) != 0:
      predefinedStr = "Hello, "
    else:
      predefinedStr = ""
    combinedStr = predefinedStr + userInput
    
  return render_template('index.html', combinedStr=combinedStr)

if __name__ == '__main__':
  app.run(debug=True)
