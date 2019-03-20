import api
import schedule
import time


import telebot
import json


with open('config.json') as f:
    config = json.load(f)


token = config['token']
admins = config['admins']


bot = telebot.TeleBot(token)


def check_db():
    mensaje_alumno = "Estimado/a {}. Le recordamos que debes abonar la cantidad de {} euros por las siguientes asignaturas: {}.\n\nAcademia MAIN."
    mensaje_admin = "\[{}] {} tiene que pagar *{}*€ por las siguientes asignaturas: \n*- {}*"
    cnx, cursor = api.conectar()
    alumnos = api.get_alumnos()
    precio = (2 * 7) * 4 # (Horas semanales * Precio hora) * Semanas
    for cid in admins:
        bot.send_message(cid, "Se va a proceder a enviar los SMS a los alumnos")
    for x in alumnos:
        if x['asignaturas']:
            for cid in admins:
                bot.send_message(cid, mensaje_admin.format(x['tlf'], x['nombre'], len(x['asignaturas']) * precio, '\n- '.join([y['siglas'] for y in x['asignaturas']])), parse_mode="Markdown")
            api.send_sms(x['tlf'], mensaje_alumno.format(x['nombre'], len(x['asignaturas']) * precio, ', '.join([y['siglas'] for y in x['asignaturas']])))
            print("Enviado SMS a {} con nº {}".format(x['nombre'], x['tlf']))
    api.desconectar(cnx, cursor)


schedule.every(30).days.at("17:05").do(check_db)


while True:
    schedule.run_pending()
    time.sleep(1)
