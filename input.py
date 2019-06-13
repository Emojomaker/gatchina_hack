import cx_Oracle
import datetime
from flask import Flask, jsonify, request
import cloudinary
import uuid
import os
import requests

os.environ["NLS_LANG"] = "American_America.AL32UTF8"

cloudinary.config(
  cloud_name = 'ddu7z1mp6',
  api_key = '318623113898338',
  api_secret = 'oVhoLqjYaCNuzL-hfsYoy0eEvqs'
)

app = Flask(__name__)


def get_current_time():
    current = datetime.datetime.now()
    current = (current.strftime("%d.%m.%Y %H:%M:%S"))
    return current


def get_photo(link):
    img_data = requests.get(link).content
    with open('/Users/a1/PycharmProjects/help_desk/images/'+str(uuid.uuid4())+'.jpg', 'wb') as handler:
        handler.write(img_data)

def tranclate_desc(text):
    text_to_translate = text
    key = 'trnsl.1.1.20190526T102718Z.3d3b72d7b2c9b3b8.f80451c53e3af46685221375aef4feb378cb99fb'
    language = 'en-ru'
    link = 'https://translate.yandex.net/api/v1.5/tr.json/translate?lang='+language+'&key='+key+'&text='+text_to_translate
    info = requests.post(url=link)
    info = ((info.content).decode('utf-8')).split('text')[-1].strip(':,",[,],}')
    return info


@app.route('/incidents/api/v1.0/create', methods=['POST'])
def create_incident():
    incident = {
        'description': request.json['description'],
        'date': get_current_time(),
        'attach': request.json['attach'],
        'user_id': request.json['user_id'],
        'gps': request.json['gps'],
        'speech_to_text': request.json['speech_to_text'],
        'priority': request.json['priority'],
        'description_on_photo': request.json['description_on_photo']
    }
    translated_text = (tranclate_desc(incident['description_on_photo']))
    conn = cx_Oracle.connect('hack','123456','192.168.137.49:1521/gdb')
    cur = conn.cursor()
    cur.execute('SELECT MAX(id)+1 from hack.input')
    sequence = cur.fetchone()
    sequence = str(sequence).strip('(,)')
    #sq = "INSERT INTO HACK.INPUT (ID, DESCRIPTION, CDATE, ATTACH, USER_ID, GPS, PRIORITY, SPEECH_TO_TEXT) VALUES ('"+sequence+"','"+translated_text+"',(to_date('"+incident['date']+"','DD.MM.YYYY hh24:mi:ss')),'"+incident['attach']+"','"+incident['user_id']+"','"+incident['gps']+"','"+incident['priority']+"','"+incident['speech_to_text']
    cur.execute("INSERT INTO HACK.INPUT (ID, DESCRIPTION, CDATE, ATTACH, USER_ID, GPS, PRIORITY, SPEECH_TO_TEXT) VALUES ('"+sequence+"','"+translated_text+"',(to_date('"+incident['date']+"','DD.MM.YYYY hh24:mi:ss')),'"+incident['attach']+"','"+incident['user_id']+"','"+incident['gps']+"','"+incident['priority']+"','"+incident['speech_to_text']+"')")
    conn.commit()
    cur.close()
    conn.close
    if incident['attach']:
        get_photo(incident['attach'])
    else:
        pass
    return jsonify({'incedint': incident}), 201


@app.route('/incidents/api/v1.0/get_incidents', methods=['GET'])
def get_incident():
    conn = cx_Oracle.connect('hack','123456','192.168.137.49:1521/gdb')
    cur = conn.cursor()
    cur.execute('SELECT CDATE, USER_ID, GPS, SPEECH_TO_TEXT FROM HACK.INCIDENT')
    return jsonify(cur.fetchall()), 201, {'Content-Type': 'text/css; charset=utf-8'}
    cur.close()
    conn.close

@app.route('/incidents/api/v1.0/get', methods=['GET'])
def get():
    conn = cx_Oracle.connect('hack','123456','192.168.137.49:1521/gdb')
    cur = conn.cursor()
    cur.execute('SELECT CDATE, USER_ID, GPS, SPEECH_TO_TEXT FROM HACK.INCIDENT')
    res = cur.fetchall()
    return jsonify(res)
    cur.close()
    conn.close


if __name__ == '__main__':
     app.run(debug=True, host='0.0.0.0')
     app.config['JSON_AS_ASCII'] = False


