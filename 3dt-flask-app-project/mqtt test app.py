import paho.mqtt.client as mqtt
from flask import Flask, render_template, request
import json
import sqlite3
import datetime

app = Flask(__name__)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("esp32/ds18b20/temperature")

def on_message(client, userdata, message):
    
    if message.topic == "esp32/ds18b20/temperature":
        #print("ds18b20 readings update")
        #print(message.payload.decode("utf-8"))
        
        ds18b20_json = message.payload.decode("utf-8")
        
        conn=sqlite3.connect('database/database.db')
        c=conn.cursor()
        datetime2 = datetime.datetime.now()
        c.execute("""INSERT INTO sensorData (temperature, currentdate, currenttime, currentDateTime, fromTopic) VALUES((?), date('now'), time('now', 'localtime'), ?, 1)""", [ds18b20_json,datetime2] )
        #print("test")
        conn.commit()
        conn.close()

mqttc=mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.connect("localhost",1883,60)
mqttc.loop_start()

@app.route("/")
def main():
    conn=sqlite3.connect('database/database.db')
    conn.row_factory = dict_factory
    c=conn.cursor()
    c.execute("SELECT * FROM sensorData ORDER BY id DESC LIMIT 20")
    readings = c.fetchall()
    #print(readings)
    return render_template('main.html', readings=readings)

if __name__ == "__main__":
    app.run(host='192.168.1.45', port=8181, debug=False)