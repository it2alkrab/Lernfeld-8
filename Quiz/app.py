from flask import Flask, render_template, request
from flask_mysqldb import MySQL
from func import *
app = Flask(__name__)

app.config['MYSQL_HOST'] = "127.0.0.1"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "quiz"

mysql = MySQL(app)

def insert_reg() :
     if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO `spieler`(`name`, `email`) VALUES (%s,%s)", (username, email))
        mysql.connection.commit()
        cur.close()
        return "seccsess"

@app.route("/", methods = ['GET','POSt'])
def home():
    insert_reg()
    return render_template('Home.html')

if __name__ == '__main__':
    app.run(debug=True)