from flask import Flask, render_template, request, redirect, url_for, flash, session, logging
import pandas
import json
import plotly
import plotly.express as px
import sqlite3
import datetime
from config import Config

from classes.sensor import Sensor

import classes.forms

config = Config()

app = Flask(__name__)

app.secret_key = config.secret_key

@app.route('/backup')
def notdash():
   Fruit = ['Apples', 'Oranges', 'Bananas', 'Apples', 'Oranges', 'Bananas']
   Amount = [4, 1, 2, 2, 4, 7]
   df = pandas.DataFrame({
      'Fruit': Fruit,
      'Amount': Amount,
      'City': ['SF', 'SF', 'SF', 'Montreal', 'Montreal', 'Montreal']
   })
   fig = px.line(df, x='Fruit', y='Amount', color='City')
   graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
   return render_template('notdash.html', graphJSON=graphJSON)

@app.route("/", methods=["GET", "POST"])
# this will only be available to logged in users
def sensorData():

    # this creates an object that contains the TopicsForm fields
    # and validation rules
    form2 = classes.forms.TopicsForm(request.form)

    # because this form submits to itself we will see if 
    # anything has been submitted and treat it differently
    # this only works if all fields have validated correctly
    if request.method == "POST" and form2.validate():

      # grab user inputs from form 
      topic = form2.topic.data
      # create a sensor object so that we can access the sensor methods
      # this comes from classes/sensor.py
      testUser = 1
      sensor = Sensor()
      # tries to get the sensor data related to the topic and will then tell user what happened
      userSensorData = sensor.retrieveSelectUserSensors(testUser,topic)
      # checks if there is any data connected to a topic and if the topic is connected to the user
      if userSensorData == "fail":
         flash("Something went wrong. No topic added to viewed topics for user: 1","danger")
         return render_template("sensorData.html",form=form2)
      elif userSensorData:
         
         df = sensor.getGraph(topic)
         fig = px.line(df, x='DateTime', y='Temperature')
         graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
         return render_template("notdash.html",graphJSON=graphJSON)
      else:
         flash("There was no data assigned to topic '"+topic+"'.","danger")
         return render_template("sensorData.html",form=form2)
    return render_template("sensorData.html",form=form2)

# runs the program
app.run(debug=False)