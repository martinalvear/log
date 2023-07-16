from flask import Flask, jsonify
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

class RegisterForm(Form):
    nombre = StringField('Nombre')
    apellido = StringField('Apellido')
    correo = StringField('Correo')
    password = StringField('Contraseña')
    id_rol = StringField('Rol')


class RoomForm(Form):
    room_nombre = StringField('Nombre de la habitacion')
    capacidad = StringField('Capacidad')
    ubicacion = StringField('Ubicación')
    precio = StringField('Precio por noche')
    imagenurl = StringField('Imagen URL')
    imagenurl2 = StringField('Imagen URL 2')
    imagenurl3 = StringField('Imagen URL 3')
    idcategoria = StringField('Categoria 1.Hotel 2.Hostal 3.Motel 4.Glamping')


@app.route('/')  
def home():
    return render_template('index.html')


@app.route('/rooms')
def rooms():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT rooms.*, ROUND(AVG(calificacion.calificacion), 1) AS promedio_calificacion, categorias.categoria FROM rooms LEFT JOIN calificacion ON rooms.id_room = calificacion.id_room JOIN categorias ON rooms.idcategoria = categorias.idcategoria GROUP BY rooms.id_room")

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
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT rooms.*, ROUND(AVG(calificacion.calificacion), 1) AS promedio_calificacion, categorias.categoria FROM rooms LEFT JOIN calificacion ON rooms.id_room = calificacion.id_room JOIN categorias ON rooms.idcategoria = categorias.idcategoria GROUP BY rooms.id_room HAVING promedio_calificacion <= 2;")

        room = cur.fetchall()
        return render_template('admin.html', room=room)
        cur.close()
    else:
        return render_template('noautorizado.html')
        #--------------------------roooooooooooooooms-----------------------

@app.route('/admin/rooms')
def admin_rooms():
    if session['id_rol'] == 1:
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT rooms.*, ROUND(AVG(calificacion.calificacion), 1) AS promedio_calificacion, categorias.categoria FROM rooms LEFT JOIN calificacion ON rooms.id_room = calificacion.id_room JOIN categorias ON rooms.idcategoria = categorias.idcategoria GROUP BY rooms.id_room")
        room = cur.fetchall()

        if result > 0:
            return render_template('admin_rooms.html', room=room)
        else:
            msg = 'No se encontraron habitaciones'
            return render_template('admin_rooms.html', msg=msg)
        cur.close()
    else:
        return render_template('noautorizado.html')
@app.route('/add_room', methods=['GET', 'POST'])
def add_room():
    if session['id_rol'] == 1:

        form = RoomForm(request.form)
        if request.method == 'POST' and form.validate():
            room_nombre = form.room_nombre.data
            capacidad = form.capacidad.data
            ubicacion = form.ubicacion.data
            precio = form.precio.data
            imagenurl = form.imagenurl.data
            imagenurl2 = form.imagenurl2.data
            imagenurl3 = form.imagenurl3.data
            idcategoria = form.idcategoria.data

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO rooms (room_nombre, capacidad, ubicacion, precio, imagenurl, imagenurl2, imagenurl3, idcategoria) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)", (room_nombre, capacidad, ubicacion, precio, imagenurl, imagenurl2, imagenurl3, idcategoria))
            mysql.connection.commit()
            cur.close()
            return redirect('/admin/rooms')
        return render_template('add_room.html', form=form)
    else:
        return render_template('noautorizado.html')


@app.route('/admin/edit_room/<string:id_room>', methods = ['GET','POST'])
def edit_room(id_room):
    if session['id_rol'] == 1:
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM rooms WHERE id_room = %s", [id_room])
        room = cur.fetchone()

        form = RoomForm(request.form)

        form.room_nombre.data = room['room_nombre']
        form.capacidad.data = room['capacidad']
        form.ubicacion.data = room['ubicacion']
        form.precio.data = room['precio']
        form.imagenurl.data = room['imagenurl']
        form.imagenurl2.data = room['imagenurl2']
        form.imagenurl3.data = room['imagenurl3']
        form.idcategoria.data = room['idcategoria']



        if request.method == 'POST' and form.validate():
            room_nombre = request.form['room_nombre']
            capacidad = request.form['capacidad']
            ubicacion = request.form['ubicacion']
            precio = request.form['precio']
            imagenurl = request.form['imagenurl']
            imagenurl2 = request.form['imagenurl2']
            imagenurl3 = request.form['imagenurl3']
            idcategoria = request.form['idcategoria']
            
            cur.execute("UPDATE rooms SET room_nombre = %s, capacidad = %s, ubicacion = %s, precio = %s, imagenurl= %s, imagenurl2 = %s, imagenurl3 = %s, idcategoria = %s WHERE id_room = %s", (room_nombre, capacidad, ubicacion, precio, imagenurl, imagenurl2, imagenurl3, idcategoria, id_room))
            mysql.connection.commit()
            cur.close()

            return redirect('/admin/rooms')
        return render_template('edit_room.html', form=form)
    else:
        return render_template('noautorizado.html')



@app.route('/admin/delete_room/<string:id_room>')
def delete_room(id_room):
    if session['id_rol'] == 1:

        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM rooms WHERE id_room = %s", [id_room])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('admin_rooms'))
    else:
        return render_template('noautorizado.html')
    
        #--------------------------end       roooooooooooooooms-----------------------
        #--------------------------useeeeeeeeeeeeeers-----------------------
@app.route('/admin/users')
def admin_users():
    if session['id_rol'] == 1:
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM usuarios")

        user = cur.fetchall()

        if result > 0:
            return render_template('admin_users.html', user=user)
        else:
            msg = 'No se encontraron usuarios'
            return render_template('admin_rooms.html', msg=msg)
        cur.close()
    else:
        return render_template('noautorizado.html')
    return render_template('admin_users.html')

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
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

        return redirect(url_for('admin_users'))
    return render_template('add_user.html', form=form)


@app.route('/admin/edit_user/<string:id>', methods = ['GET','POST'])
def edit_user(id):
    if session['id_rol'] == 1:
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM usuarios WHERE id = %s", [id])
        user = cur.fetchone()

        form = RegisterForm(request.form)

        form.nombre.data = user['nombre']
        form.apellido.data = user['apellido']
        form.correo.data = user['correo']
        form.password.data = user['password']
        form.id_rol.data = user['id_rol']




        if request.method == 'POST' and form.validate():
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            correo = request.form['correo']
            password = request.form['password']
            id_rol = request.form['id_rol']

            cur.execute("UPDATE usuarios SET nombre = %s, apellido = %s, correo = %s, password = %s, id_rol = %s WHERE id = %s", (nombre, apellido, correo, password, id_rol, id))
            mysql.connection.commit()
            cur.close()

            return redirect('/admin/users')
        return render_template('edit_user.html', form=form)
    else:
        return render_template('noautorizado.html')



@app.route('/admin/delete_user/<string:id>')
def delete_user(id):
    if session['id_rol'] == 1:

        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM usuarios WHERE id = %s", [id])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('admin_users'))
    else:
        return render_template('noautorizado.html')



        #--------------------------useeeeeeeeeeeeeers-----------------------


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
                    cur = mysql.connection.cursor()
                    result = cur.execute("SELECT rooms.*, ROUND(AVG(calificacion.calificacion), 1) AS promedio_calificacion FROM rooms LEFT JOIN calificacion ON rooms.id_room = calificacion.id_room WHERE calificacion.id_room < 3 GROUP BY rooms.id_room")

                    room = cur.fetchall()

                    if result > 0:
                        return render_template('admin.html', room=room)
                    else:
                        msg = 'No se encontraron habitaciones'
                        return render_template('admin.html', msg=msg)
                    cur.close()

                    return render_template("admin.html")
                    return render_template("admin.html")
            elif session['id_rol'] == 2:
                    cur = mysql.connection.cursor()
                    result = cur.execute("SELECT rooms.*, ROUND(AVG(calificacion.calificacion), 1) AS promedio_calificacion FROM rooms LEFT JOIN calificacion ON rooms.id_room = calificacion.id_room WHERE calificacion.id_room > 3 GROUP BY rooms.id_room")

                    room = cur.fetchall()

                    if result > 0:
                        return render_template('user.html', room=room)
                    else:
                        msg = 'No se encontraron habitaciones'
                        return render_template('user.html', msg=msg)
                    cur.close()

            return render_template("user.html")
        else:
            return render_template('index.html', mensaje="Usuario O Contraseña Incorrectas")

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

#--------------user---------------------------------------------------------------
@app.route('/user', methods=['GET'])
def user():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT rooms.*, ROUND(AVG(calificacion.calificacion), 1) AS promedio_calificacion FROM rooms LEFT JOIN calificacion ON rooms.id_room = calificacion.id_room WHERE calificacion.id_room > 3 GROUP BY rooms.id_room HAVING promedio_calificacion > 3.5 ORDER BY promedio_calificacion DESC;")
    room = cur.fetchall()
    cur.close()

    return render_template('user.html', room=room)


@app.route('/room/<string:id_room>')
def view_room(id_room):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT rooms.*, ROUND(AVG(calificacion.calificacion), 1) AS promedio_calificacion, categorias.categoria FROM rooms LEFT JOIN calificacion ON rooms.id_room = calificacion.id_room JOIN categorias ON rooms.idcategoria = categorias.idcategoria WHERE rooms.id_room = %s GROUP BY rooms.id_room", [id_room])
    
    room = cur.fetchall()
    return render_template('view_room.html', room=room)
    cur.close()

@app.route('/formulariocalificacion', methods=['GET'])
def mostrar_formulario():
    
    return render_template('calificacion.html')

@app.route('/calificaciones', methods=['GET','POST'])
def insertar_calificacion():
    calificacion = request.form.get('calificacion')
    fecha = request.form.get('fecha')
    id = request.form.get('idusuario')
    id_room = request.form.get('idhabitacion')

    # Aquí puedes realizar las operaciones necesarias para insertar la calificación en tu base de datos

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO calificacion(calificacion, fecha, id, id_room) VALUES(%s,%s,%s,%s)",
                    (calificacion, fecha, id, id_room))
    mysql.connection.commit()
    cur.close()
    return render_template('exitoso.html')

@app.route('/mejores_habitaciones', methods=['POST'])
def mostrar_habitaciones_mejor_calificadas():
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT rooms.*, ROUND(AVG(calificacion.calificacion), 1) AS promedio_calificacion FROM rooms LEFT JOIN calificacion ON rooms.id_room = calificacion.id_room WHERE calificacion.fecha BETWEEN %s AND %s GROUP BY rooms.id_room ORDER BY promedio_calificacion DESC", (fecha_inicio, fecha_fin))
    room = cur.fetchall()
    cur.close()

    return render_template('habitaciones.html', room=room)

@app.route('/buscar_calificaciones', methods=['GET'])
def mostrar_formulario_busqueda():
    return render_template('formulario_busqueda.html')




##
@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT rooms.*, ROUND(AVG(calificacion.calificacion), 1) AS promedio_calificacion, categorias.categoria FROM rooms LEFT JOIN calificacion ON rooms.id_room = calificacion.id_room JOIN categorias ON rooms.idcategoria = categorias.idcategoria GROUP BY rooms.id_room")

    room_data = cur.fetchall()
    cur.close()

    return jsonify(room_data)

@app.route('/api/users')
def get_users():
    
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM usuarios")

    user = cur.fetchall()
    cur.close()
    return jsonify(user)

@app.route('/api/mejores_habitaciones', methods=['GET'])
def get_mostrar_habitaciones_mejor_calificadas():
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT rooms.*, ROUND(AVG(calificacion.calificacion), 1) AS promedio_calificacion FROM rooms LEFT JOIN calificacion ON rooms.id_room = calificacion.id_room WHERE calificacion.fecha BETWEEN %s AND %s GROUP BY rooms.id_room ORDER BY promedio_calificacion DESC", (fecha_inicio, fecha_fin))
    room = cur.fetchall()
    cur.close()

    return jsonify(room)





if __name__ == '__main__':
    app.secret_key = "pinchellave"
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
