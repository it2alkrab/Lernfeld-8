from flask_mysqldb import MySQL
from flask import Flask, render_template, request, redirect, url_for, session
import MySQLdb.cursors
import re
app = Flask(__name__)

app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = "127.0.0.1"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "quiz"

mysql = MySQL(app)


@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM spieler WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)
 
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
 
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM spieler WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO `spieler`(`username`, `password`,`email`) VALUES (% s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

@app.route("/anzeigen")
def anzeigen():
    # Daten aus der Datenbank lesen
    cur = mysql.connection.cursor()
    cur.execute("SELECT `id`, `frage`, `antwort1`, `antwort2`, `antwort3`, `antwort4`, `Korrekte_antwort`, `kategorie_id` FROM `fragen` WHERE 1;")
    fragen = cur.fetchall()
    cur.close()
    print(fragen)
    # Daten an die Vorlage übergeben
    return render_template("anzeigen.html", fragen=fragen)


@app.route("/bearbeiten_fragen")
def bearbeiten_fragen():
    fragen_liste = []
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM fragen")
    for row in cursor:
        frage_dict = dict(zip([col[0] for col in cursor.description], row))
        fragen_liste.append(frage_dict)
    cursor.close()
    return render_template("bearbeiten_fragen.html", fragen_liste=fragen_liste)

@app.route("/bearbeiten_fragen/<int:id>", methods=['GET', 'POST'])
def bearbeiten_fragen_id(id):
    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM fragen WHERE id = %s", (id,))
        frage = cursor.fetchone()
        cursor.close()
        print(frage)
        return render_template("bearbeiten_fragen_id.html", frage=frage)
    elif request.method == 'POST':
        frage = request.form['frage']
        antwort1 = request.form['antwort1']
        antwort2 = request.form['antwort2']
        antwort3 = request.form['antwort3']
        antwort4 = request.form['antwort4']
        korrekte_antwort = request.form['korrekte_antwort']
        kategorie_id = request.form['kategorie_id']
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE fragen
            SET frage = %s, antwort1 = %s, antwort2 = %s, antwort3 = %s,
            antwort4 = %s, korrekte_antwort = %s, kategorie_id = %s
            WHERE id = %s
            """, (frage, antwort1, antwort2, antwort3, antwort4, korrekte_antwort, kategorie_id, id))
        cursor.connection.commit()
        cursor.close()
        return redirect(url_for("bearbeiten_fragen"))




if __name__ == '__main__':
    app.run(debug=True)