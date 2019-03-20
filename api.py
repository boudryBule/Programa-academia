def conectar():
    """
    Función para conectarnos a la base de datos.
    Primero importamos el módulo sqlite3  porque estamos usando la base de datos de sqlite3
    Hacemos la conexión a nuestra base de datos bd.db
    Generamos el cursor con el que haremos las consultas a la  base de datos
    Devolvemos el objeto de la conexión y el cursor
    """
    import sqlite3
    cnx = sqlite3.connect('bd.db')
    cursor = cnx.cursor()
    return cnx, cursor


def desconectar(cnx, cursor):

    """
    Función para desconectarnos de la base de datos
    Primero cerramos el cursor y luego la conexión

    """
    cursor.close()
    cnx.close()


def get_alumno_id(nombre, tlf):
    cnx, cursor = conectar() #Primero nos conectamos a la base de datos    
    tmp_1 = cursor.execute("SELECT id FROM alumno WHERE nombre = \"{}\" AND tlf = \"{}\";".format(nombre, tlf)).fetchall()
    desconectar(cnx, cursor)
    return tmp_1[0][0]


def get_alumno(id):
    cnx, cursor = conectar() #Primero nos conectamos a la base de datos    
    tmp_1 = cursor.execute("""
SELECT id, nombre, tlf
FROM alumno
WHERE id = {};
""".format(id)).fetchall()[0]
    alumno = {
        'id': tmp_1[0],
        'nombre': tmp_1[1],
        'tlf': tmp_1[2],
        'asignaturas': []
    }
    tmp_2 = cursor.execute("""
SELECT a.id, a.nombre
FROM alumnoasignatura aa, asignatura a
WHERE
    aa.idAlumno = "{}"
AND
    aa.idAsignatura = a.id;
""".format(alumno['id'])).fetchall()
    for x in tmp_2:
        alumno['asignaturas'].append({
            'id': x[0],
            'nombre': x[1]
        })
    desconectar(cnx, cursor)
    return alumno


def tiene_asignatura(id_alumno, id_asignatura):
    cnx, cursor = conectar()
    tmp_1 = cursor.execute("""
SELECT *
FROM alumnoasignatura
WHERE 
    idAlumno = "{}"
AND
    idAsignatura = "{}"
""".format(id_alumno, id_asignatura)).fetchall()
    desconectar(cnx, cursor)
    return True if tmp_1 else False


def get_alumnos():

    """
    Función para obtener los alumnos

    """
    cnx, cursor = conectar() #Primero nos conectamos a la base de datos
    alumnos = [] #Crea una lista vacía donde guardaremos los alumnos
    tmp_1 = cursor.execute("""
SELECT id, nombre, tlf
FROM alumno;
""") #Guardamos en una variale temporal el id,nombre y telefono de nuestros alumnos
    for x in [x for x in tmp_1.fetchall()]: #recorremos la lista
        tmp_2 = cursor.execute("""
SELECT a.id, a.nombre, a.siglas
FROM alumnoasignatura aa, asignatura a
WHERE
    aa.idAlumno = "{}"
AND
    aa.idAsignatura = a.id;
""".format(x[0])) #por cada alumno cogemos el id de la asignatura y el nombre
        c = {
            'id': x[0],
            'nombre': x[1],
            'tlf': x[2],
            'asignaturas': []
        } #Guardamos en un diccionario la información del alumno en cuestión
        asignaturas = tmp_2.fetchall() #metemos en asignatura todo lo que nos haya devuelto  la última consulta
        for y in asignaturas: #recorremos las asignaturas
            c['asignaturas'].append({
                'id': y[0],
                'nombre': y[1],
                'siglas': y[2]
            })  #en cada alumno metemos sus asignaturas
        alumnos.append(c) #lo guardamos en la variable alumnos
    desconectar(cnx, cursor) #nos desconectamos de la base de datos
    return alumnos #devolvemos los alumnos

def add_alumno(nombre, tlf):
    """
        Función para añadir alumno
    """
    cnx, cursor = conectar()
    cursor.execute("""
INSERT INTO alumno (nombre, tlf)
VALUES ("{}", "{}");
""".format(nombre, tlf)) #Guardamos el nombre y el teléfono del nuevo alumno
    cnx.commit() #hacemos commit para que se guarden los cambios en la base de datos
    desconectar(cnx, cursor)
    return "Alumno añadido correctamente"


def get_asignaturas():
    cnx, cursor = conectar()
    tmp_1 = cursor.execute("SELECT id, nombre, siglas FROM asignatura").fetchall()
    asignaturas = []
    for x in tmp_1:
        asignaturas.append(
            {
                "id": x[0],
                "nombre": x[1],
                "siglas": x[2]
            }
        )
    desconectar(cnx, cursor)
    return asignaturas

def del_alumno(id_alumno):
    cnx, cursor = conectar()
    cursor.execute("""
DELETE FROM alumnoAsignatura
WHERE idAlumno = "{}";
""")
    cursor.execute("""
DELETE FROM alumno
WHERE id = "{}";
""".format(id_alumno))
    cnx.commit()
    desconectar(cnx, cursor)


def add_asignatura_base(nombre, siglas):
    cnx, cursor = conectar()
    cursor.execute("""
INSERT INTO asignatura (nombre, siglas)
VALUES ("{}", "{}");
""".format(nombre, siglas))
    cnx.commit()
    desconectar(cnx, cursor)
    return "Asignatura añadida correctamente"


def del_asignatura_base(id_asignatura):
    cnx, cursor = conectar()
    cursor.execute("""
DELETE FROM alumnoAsignatura
WHERE idAsignatura = "{}";
""".format(id_asignatura))
    cursor.execute("""
DELETE FROM asignatura
WHERE id = "{}";
""".format(id_asignatura))
    cnx.commit()
    desconectar(cnx, cursor)
    return "Asignatura borrada correctamente"


def add_asignatura(id_alumno, id_asignatura):
    cnx, cursor = conectar()
    cursor.execute("""
INSERT INTO alumnoAsignatura (idAlumno, idAsignatura)
VALUES ("{}", "{}");
""".format(id_alumno, id_asignatura))
    cnx.commit()
    desconectar(cnx, cursor)
    return "Asignatura añadida correctamente"


def del_asignatura(id_alumno, id_asignatura):
    cnx, cursor = conectar()
    cursor.execute("""
DELETE FROM alumnoAsignatura
WHERE
    idAlumno = "{}"
AND
    idAsignatura = "{}";
""".format(id_alumno, id_asignatura))
    cnx.commit()
    desconectar(cnx, cursor)

def send_sms(numero, texto):
    from datetime import datetime
    import os
    cnx, cursor = conectar()
    cursor.execute("""
INSERT INTO sms (numero, texto, fecha)
VALUES ("{}", "{}", "{}");
""".format(numero, texto, str(datetime.now())))
    a = os.popen('echo "{}" | sudo gammu sendsms TEXT 0034{}'.format(texto, numero)).read()
    cnx.commit()
    desconectar(cnx, cursor)
    return a

def get_sms():
    cnx, cursor = conectar()
    sms = {}
    for x in cursor.execute("SELECT * FROM sms;").fetchall():
        sms[x[0]] = {'numero': x[1], 'texto': x[2], 'fecha': x[3]}
    desconectar(cnx, cursor)
    return sms
