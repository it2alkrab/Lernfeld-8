from flask import request

def insert_reg() :
     if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO `spieler`(`name`, `email`) VALUES (%s,%s)", (username, email))
        mysql.connection.commit()
        cur.close()
        return "seccsess"