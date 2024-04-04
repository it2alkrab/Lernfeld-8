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
def index():
    if 'loggedin' in session and session['loggedin'] == True:
        return render_template('home.html')
    else:
        return redirect(url_for('login'))


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
            return render_template('home.html', msg = msg)
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
    # Kategorien auslesen
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM kategorien")
    kategorien = cur.fetchall()
    cur.close()

    # Frage auswählen abhängig von der Kategorie (optional)
    selected_category = request.args.get('kategorie_id')

    if selected_category:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM fragen WHERE kategorie_id = %s", (selected_category,))
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM fragen")

    fragen = cur.fetchall()
    cur.close()

    return render_template("anzeigen.html", kategorien=kategorien, fragen=fragen)

@app.route("/kategorien")
def kategorien():
  kategorien = []
  cursor = mysql.connection.cursor()
  cursor.execute("SELECT * FROM kategorien")
  for row in cursor:
    kategorie_dict = dict(zip([col[0] for col in cursor.description], row))
    kategorien.append(kategorie_dict)
  cursor.close()
  return render_template("kategorie_auswählen.html", kategorien=kategorien)

@app.route("/spielen", methods=["GET", "POST"])
def spielen():
  if request.method == "GET":
    return render_template("kategorie_auswählen.html")
  elif request.method == "POST":
    kategorie_id = request.form.get("kategorie_id")

    # Validierung der Kategorie-ID
    if not kategorie_id or not kategorie_id.isdigit():
      return render_template("fehlermeldung.html", 
                            meldung="Ungültige Kategorie-ID")

    # Zufällige Frage aus der gewählten Kategorie laden
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM fragen WHERE kategorie_id = %s ORDER BY RAND() LIMIT 1", (kategorie_id,))
    frage = cursor.fetchone()
    cursor.close()

    if not frage:
      # Fehlermeldung anzeigen, falls keine Fragen vorhanden
      return render_template("keine_fragen.html")

    return render_template("spielen.html", frage=frage)

@app.route("/auswertung", methods=["POST"])
def auswertung():
    # Ausgewählte Antwort auswerten
    antwort_id = request.form.get("antwort_id")
 
    # Korrekte Antwort aus der Datenbank laden
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT korrekte_antwort FROM fragen WHERE id = %s", (antwort_id,))
    richtige_antwort = cursor.fetchone()
    cursor.close()
 
    # Ergebnis ermitteln
    richtig_falsch = "richtig" if antwort_id == richtige_antwort else "falsch"
 
    # Nächste Frage laden
    kategorie_id = request.form.get("kategorie_id")
    fragen = []
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT * FROM fragen 
        WHERE kategorie_id = %s 
        ORDER BY RAND() LIMIT 1
        """, (kategorie_id,))
    frage = cursor.fetchone()
    cursor.close()
 
    if not frage:
        # Fehlermeldung anzeigen, falls keine Fragen vorhanden
        return render_template("keine_fragen.html")
 
    # Punkte des Benutzers berechnen (optional)
    # ... Code zur Punkteberechnung ...
 
    # Ergebnis an die Vorlage übergeben
    return render_template("ergebnis.html",
                          richtig_falsch=richtig_falsch,
                          richtige_antwort=richtige_antwort,
                          frage=frage,
                          )

@app.route("/neue_frage", methods=["GET", "POST"])
def neue_frage():
  if request.method == "GET":
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM kategorien")
    kategorien = cursor.fetchall()
    cursor.close()
    return render_template("neue_frage.html" , kategorien=kategorien)
  elif request.method == "POST":
    frage = request.form.get("frage")
    antwort1 = request.form.get("antwort1")
    antwort2 = request.form.get("antwort2")
    antwort3 = request.form.get("antwort3")
    antwort4 = request.form.get("antwort4")
    korrekte_antwort = request.form.get("korrekte_antwort")
    kategori = request.form.get("kategori")

    # Validierung der eingegebenen Daten (optional)

    cursor = mysql.connection.cursor()
    cursor.execute("""
      INSERT INTO fragen (frage, antwort1, antwort2, antwort3, antwort4, korrekte_antwort)
      VALUES (%s, %s, %s, %s, %s, %s)
    """, (frage, antwort1, antwort2, antwort3, antwort4, korrekte_antwort, kategori))
    mysql.connection.commit()
    cursor.close()

    

    # Bestätigungsmeldung oder Weiterleitung zur Fragenübersicht
    return render_template("erfolg.html", meldung="Kategorie erfolgreich hinzugefügt")

@app.route("/neue_kategorie", methods=["GET", "POST"])
def neue_kategorie():
  if request.method == "GET":
    return render_template("neue_kategorie.html")
  elif request.method == "POST":
    name = request.form.get("name")

    # Validierung des Kategoriennamens (optional)

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO kategorien (name) VALUES (%s)", (name,))
    mysql.connection.commit()
    cursor.close()

    # Bestätigungsmeldung oder Weiterleitung
    return render_template("erfolg.html", meldung="Kategorie erfolgreich hinzugefügt")





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

@app.route("/rangliste")
def rangliste():
  cursor = mysql.connection.cursor()
  cursor.execute("""
    SELECT 
      name, 
      punkte, 
      RANK() OVER (ORDER BY punkte DESC) AS platz
    FROM 
      spieler 
    ORDER BY 
      punkte DESC
  """)
  rangliste = cursor.fetchall()
  cursor.close()

  return render_template("rangliste.html", rangliste=rangliste)





if __name__ == '__main__':
    app.run(debug=True)