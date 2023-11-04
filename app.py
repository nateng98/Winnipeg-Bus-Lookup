from flask import Flask, render_template, request
import pyodbc

app = Flask(__name__)

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
