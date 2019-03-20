import telebot
from telebot import types
import api
import json


with open('config.json') as f:
    config = json.load(f)


token = config['token']
admins = config['admins']


bot = telebot.TeleBot(token)


user_step = dict()


info_alumno = {
    'nombre': None,
    'tlf': None
}

info_asignatura = {
    'nombre': None,
    'siglas': None
}


def get_user_step(cid):
    return user_step.get(str(cid))


def generar_teclado_alumnos():
    alumnos = api.get_alumnos()
    teclado = types.InlineKeyboardMarkup(row_width=1)
    for x in alumnos:
        boton = types.InlineKeyboardButton(x['nombre'], callback_data="alumno {}".format(x['id']))
        teclado.add(boton)
    return teclado


def generar_teclado_asignaturas(id_alumno = None):
    teclado = types.InlineKeyboardMarkup(row_width=1)
    asignaturas = api.get_asignaturas()
    if not id_alumno:
        alumno = api.get_alumno_id(info_alumno['nombre'], info_alumno['tlf'])
    else:
        alumno = id_alumno
    for x in asignaturas:
        boton = types.InlineKeyboardButton(x['nombre'], callback_data="add {} {}".format(x['id'], alumno))
        teclado.add(boton)
    teclado.row_width = 2
    boton1 = types.InlineKeyboardButton("Terminar", callback_data="terminar {}".format(alumno))
    boton2 = types.InlineKeyboardButton("Borrar Alumno", callback_data="borrar {}".format(alumno))
    teclado.add(boton1, boton2)
    return teclado


def generar_teclado_asignaturas_2():
    teclado = types.InlineKeyboardMarkup(row_width=1)
    asignaturas = api.get_asignaturas()
    for x in asignaturas:
        boton = types.InlineKeyboardButton(x['nombre'], callback_data='del {}'.format(x['id']))
        teclado.add(boton)
    boton1 = types.InlineKeyboardButton("Terminar", callback_data='finalizado')
    teclado.add(boton1)
    return teclado


@bot.message_handler(commands=['cancelar'])
def handler_cancelar(m):
    cid = m.chat.id
    bot.send_message(cid, "Cancelado cualquier comando en ejecución.", reply_markup=types.ReplyKeyboardRemove())
    user_step[str(cid)] = None


@bot.callback_query_handler(func=lambda call: call.data.startswith('alumno'))
def callback_alumno(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    info = call.data.split()
    alumno = info[1]
    alumno_info = api.get_alumno(alumno)
    teclado_asignaturas = generar_teclado_asignaturas(alumno)
    mensaje = "Asignaturas de *{}*:\n\n".format(alumno_info['nombre'])
    for x in alumno_info['asignaturas']:
        mensaje += " - *{}*\n".format(x['nombre'])
    bot.edit_message_text(mensaje, cid, mid, reply_markup=teclado_asignaturas, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: call.data.startswith('add'))
def callback_add(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    info = call.data.split()
    asignatura = info[1]
    alumno = info[2]
    alumno_info = api.get_alumno(alumno)
    if api.tiene_asignatura(alumno, asignatura):
        api.del_asignatura(alumno, asignatura)
    else:
        api.add_asignatura(alumno, asignatura)
    teclado_asignaturas = generar_teclado_asignaturas(alumno)
    alumno_info = api.get_alumno(alumno)
    mensaje = "Asignaturas de *{}*:\n\n".format(alumno_info['nombre'])
    for x in alumno_info['asignaturas']:
        mensaje += " - *{}*\n".format(x['nombre'])
    bot.edit_message_text(mensaje, cid, mid, reply_markup=teclado_asignaturas, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: call.data.startswith('terminar'))
def callback_terminar(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    info = call.data.split()
    alumno = info[1]
    alumno_info = api.get_alumno(alumno)
    mensaje = "Asignaturas de *{}*:\n\n".format(alumno_info['nombre'])
    for x in alumno_info['asignaturas']:
        mensaje += " - *{}*\n".format(x['nombre'])
    bot.edit_message_text(mensaje, cid, mid, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: call.data.startswith('borrar'))
def callback_borrar(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    info = call.data.split()
    alumno = info[1]
    alumno_info = api.get_alumno(alumno)
    api.del_alumno(alumno)
    mensaje = "Borrado el alumno *{}*".format(alumno_info['nombre'])
    bot.edit_message_text(mensaje, cid, mid, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: call.data.startswith('del'))
def callback_del(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    id_asignatura = call.data.split()[1]
    api.del_asignatura_base(id_asignatura)
    bot.edit_message_text("Haz click en las asignaturas para borrarlas.", cid, mid, reply_markup=generar_teclado_asignaturas_2())


@bot.callback_query_handler(func=lambda call: call.data.startswith('finalizado'))
def callback_finalizado(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    bot.edit_message_text("Fin de borrado de asignaturas.", cid, mid)


@bot.message_handler(commands=['start'])
def handle_start(m):
    cid = m.chat.id
    bot.send_message(cid, "Bienvenido al bot mákina")


@bot.message_handler(commands=['add_alumno'])
def handle_add_alumno(m):
    cid = m.chat.id
    bot.send_message(cid, "Dime el nombre del alumno.", reply_markup=types.ForceReply())
    user_step[str(cid)] = 'add_alumno'


@bot.message_handler(func=lambda m: get_user_step(m.chat.id) == 'add_alumno')
def step_add_alumno(m):
    cid = m.chat.id
    nombre = m.text
    info_alumno['nombre'] = nombre
    bot.send_message(cid, "Dime el teléfono de {}".format(nombre), reply_markup=types.ForceReply())
    user_step[str(cid)] = 'add_tlf'


@bot.message_handler(func=lambda m: get_user_step(m.chat.id) == 'add_tlf')
def step_add_tlf(m):
    cid = m.chat.id
    tlf = m.text
    info_alumno['tlf'] = tlf
    api.add_alumno(info_alumno['nombre'], info_alumno['tlf'])
    bot.send_message(cid, "Añadido correctamente el siguiente alumno:\nNombre: {}\nTeléfono: {}".format(info_alumno['nombre'], info_alumno['tlf']))
    teclado_asignaturas = generar_teclado_asignaturas()
    bot.send_message(cid, "Haz click en las asignaturas para añadirlas o borrarlas al alumno.", reply_markup=teclado_asignaturas)
    user_step[str(cid)] = None


@bot.message_handler(commands=['get_alumnos'])
def handler_get_alumnos(m):
    cid = m.chat.id
    mensaje = "Pulsa sobre el nombre del alumno para mostrar su información."
    teclado_alumnos = generar_teclado_alumnos()
    bot.send_message(cid, mensaje, reply_markup=teclado_alumnos, parse_mode="Markdown")


@bot.message_handler(commands=['get_asignaturas'])
def handler_get_asignaturas(m):
    cid = m.chat.id
    mensaje = "Estas son las asignaturas que ya existen:\n\n"
    asignaturas = api.get_asignaturas()
    for x in asignaturas:
        mensaje += " - *{}*\n".format(x['nombre'])
    bot.send_message(cid, mensaje, parse_mode="Markdown")


@bot.message_handler(commands=['add_asignatura'])
def handler_add_asignatura(m):
    cid = m.chat.id
    mensaje = "Estas son las asignaturas que ya existen:\n\n"
    asignaturas = api.get_asignaturas()
    for x in asignaturas:
        mensaje += " - *{}*\n".format(x['nombre'])
    mensaje += "\nEscribe el nombre de la nueva asignatura o pulsa /cancelar para no añadir nuevas."
    bot.send_message(cid, mensaje, reply_markup=types.ForceReply(), parse_mode="Markdown")
    user_step[str(cid)] = 'add_asignatura'


@bot.message_handler(func=lambda m: get_user_step(m.chat.id) == 'add_asignatura')
def step_add_asignatura(m):
    cid = m.chat.id
    nombre = m.text
    info_asignatura['nombre'] = nombre
    bot.send_message(cid, "Dime las siglas de *{}*".format(nombre), reply_markup=types.ForceReply(), parse_mode="Markdown")
    user_step[str(cid)] = 'add_siglas'

@bot.message_handler(commads=['del_asignatura'])
def handler_del_asignatura(m):
    cid = m.chat.id
    bot.send_message(cid, "Haz click en las asignaturas para borrarlas.", reply_markup=generar_teclado_asignaturas_2())

@bot.message_handler(func=lambda m: get_user_step(m.chat.id) == 'add_siglas')
def step_add_siglas(m):
    cid = m.chat.id
    siglas = m.text.upper()
    info_asignatura['siglas'] = siglas
    api.add_asignatura_base(info_asignatura['nombre'], info_asignatura['siglas'])
    bot.send_message(cid, "Añadida asignatura correctamente.")
    user_step[str(cid)] = None


@bot.message_handler(commands=['send_sms'], func=lambda m: m.text and len(m.text.split()) > 2)
def handler_send_sms(m):
    cid = m.chat.id
    texto = m.text
    tlf = texto.split()[1]
    mensaje = texto.split(tlf)[1].strip()
    api.send_sms(tlf, mensaje)
    bot.send_message(cid, "Enviado a {}:\n\n{}".format(tlf, mensaje))


@bot.message_handler(commands=['get_sms'])
def handler_get_sms(m):
    cid = m.chat.id
    mensajes = api.get_sms()
    phone = "📱"
    txt = "✉️"
    calendar = "📆"
    msg = "Mensajes enviados:\n"
    for y, x in mensajes.items():
        msg += "{}: {}\n{}: {}\n{}: {}\n\n".format(phone, x['numero'], txt, x['texto'], calendar, x['fecha'].split()[0])
    bot.send_message(cid, msg)


bot.polling()
