from flask import Flask
from flask import render_template, request, redirect, Response, url_for, session, flash
from flask_mysqldb import MySQL, MySQLdb  # pip install Flask-MySQLdb
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__, template_folder='template')

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'udla1'
app.config['MYSQL_DB'] = 'flaskMVC'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/rooms')
def rooms():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM rooms")

    room = cur.fetchall()

    if result > 0:
        return render_template('rooms.html', room=room)
    else:
        msg = 'No se encontraron habitaciones'
        return render_template('rooms.html', msg=msg)
    cur.close()


#---ADMIN----
@app.route('/admin')
def admin():
    if session['id_rol'] == 1:
        return render_template('admin.html')
    else:
        return "NO AUTORIZADO"

@app.route('/admin/rooms')
def admin_rooms():
    if session['id_rol'] == 1:
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM rooms")

        room = cur.fetchall()

        if result > 0:
            return render_template('admin_rooms.html', room=room)
        else:
            msg = 'No se encontraron habitaciones'
            return render_template('admin_rooms.html', msg=msg)
        cur.close()
    else:
        return "NO AUTORIZADO"
#---------END ADMIN------
@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada', 'success')
    return redirect(url_for('home'))

@app.route('/acceso-login', methods=["GET", "POST"])
def login():

    if request.method == 'POST' and 'txtCorreo' in request.form and 'txtPassword' in request.form:

        _correo = request.form['txtCorreo']
        _password = request.form['txtPassword']

        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM usuarios WHERE correo = %s AND password = %s', (_correo, _password,))
        account = cur.fetchone()

        if account:
            session['logueado'] = True
            session['id'] = account['id']
            session['id_rol'] = account['id_rol']

            if session['id_rol'] == 1:
                return render_template("admin.html")
            elif session['id_rol'] == 2:
                return render_template("user.html")
        else:
            return render_template('index.html', mensaje="Usuario O Contraseña Incorrectas")


class RegisterForm(Form):
    nombre = StringField('Nombre')
    apellido = StringField('Apellido')
    correo = StringField('Correo')
    password = PasswordField('Contraseña')
    id_rol = StringField('Email')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        nombre = form.nombre.data
        apellido = form.apellido.data
        correo = form.correo.data
        password = form.password.data
        id_rol = form.id_rol.data
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuarios(nombre, apellido, correo, password, id_rol) VALUES(%s,%s,%s,%s,%s)",
                    (nombre, apellido, correo, password, id_rol))
        mysql.connection.commit()
        cur.close()

        flash('Registrado correctamente', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', form=form)


@app.route('/admin/user')
def admin_user():
    if session['id_rol'] == 1:
        return "USUARIOS"
    else:
        return 'NO AUTORIZADO'


if __name__ == '__main__':
    app.secret_key = "pinchellave"
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
