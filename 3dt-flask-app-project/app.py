# import flash application
from flask import Flask, render_template, request, redirect, url_for, flash, session, logging
# import our config file config.py
from config import Config
# import functools
from functools import wraps 
# import our classes in the classes folder
from classes.user import User
from classes.sensor import Sensor

import classes.forms

# libaries used for commented out mqtt program whilst on laptop and not needing testing the progrma with data
import paho.mqtt.client as mqtt
import json
import sqlite3

#libaries for graph
import plotly
import plotly.express as px

# library to get datetime as one thing easily
import datetime

# create an object with our Config class properties
config = Config()

# instantiate flask
app = Flask(__name__)

# set the secret key for encryption
app.secret_key = config.secret_key

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # connects to the database
    conn=sqlite3.connect('database/database.db')
    c=conn.cursor()
    # finds all topics
    c.execute("SELECT topics.topic FROM topics")
    topics = c.fetchall()
    # goes through every topic
    for topic in topics:
        # turns topic into str 
        topic_str = str(topic)
        topic2 = topic_str.replace("(","").replace("'","").replace(",","").replace(")","")
        # subscribes to the topic
        client.subscribe(topic2)
    # closes databse connection
    conn.close()


def on_message(client, userdata, message):
    # connects to the database
    conn=sqlite3.connect('database/database.db')
    c=conn.cursor()
    # finds all topics
    c.execute("SELECT topics.topic FROM topics")
    topics = c.fetchall()
    # goes through every topic
    for topic in topics:
        # turns topic into a string
        topic_str = str(topic)
        topic2 = topic_str.replace("(","").replace("'","").replace(",","").replace(")","")
        # checks what topic message is recieved from
        if message.topic == topic2:
            # testing
            #print("ds18b20 readings update")
            #print(message.payload.decode("utf-8"))
            # decodes the message
            ds18b20_json = message.payload.decode("utf-8")
            # gets topics id to connect to database
            c.execute("SELECT topics.id FROM topic WHERE topics.topic = ?",[topic2])
            topicID = c.fetchone()
            # gets time info in variables I need
            currentDateTime = datetime.datetime.now()
            currentDate = currentDateTime.strftime("%Y-%m-%d")
            currentTime = currentDateTime.strftime("%H:%M:%S")
            # turns topicID into a integer
            topicID = str(topicID).replace("(","").replace(",","").replace(")","")
            topicID = int(topicID)
            # inserts data into database
            c.execute("""INSERT INTO sensorData (temperature, currentdate, currenttime, currentDateTime, fromTopic) VALUES(?, ?, ?, ?, ?)""", [ds18b20_json,currentDate,currentTime,currentDateTime,topicID] )
            #print("test")
            # commits data insert
            conn.commit()
            # closes database connection
            conn.close()

# mqtt system to get data from arduino 
mqttc=mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.connect("localhost",1883,60)
mqttc.loop_start()

# checks if user is logged in
def is_loggged_in(f):
    @wraps(f)
    # We use *args and **kwargs because we don't know how many
    # parameters (arguements) will be passed to each function
    # that we're testing.
    def wrap(*args,**kwargs):
        # if the user is logged in then it's business as usual
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            # if the user isn't logged in then flash them a message
            # and boot them out to the login page.
            flash("Unauthorised access. Please log in.","danger")
            return redirect(url_for('login'))
    return wrap

# home page
@app.route("/")
def home():

    # this reaches into template folder and renders the home.html page
    return render_template("home.html")

# user page
@app.route("/user")
# this will only be available to logged in users
@is_loggged_in
def user():

    
    return render_template("user.html", name=session['username'])
    

#register page
@app.route("/register", methods=["GET", "POST"])
def register():

    # this creates an object that contains the RegisterForm fields
    # and validation rules
    form = classes.forms.RegisterForm(request.form)

    # because this form submits to itself we will see if 
    # anything has been submitted and treat it differently
    # this only works if all fields have validated correctly
    if request.method == "POST" and form.validate():

        # grab user inputs from form 
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # create a user object so that we can access the user methods
        # this comes from classes/user.py
        user = User()

        # here we call the insertUser method on the user class
        # it will return a boolean of either True or False
        success = user.insertUser(username,password,email)

        # if success: is the same thing as if success == True
        if success:
            # if user successfully registers we let them know and send them to login
            flash("You have now registered.","success")
            return redirect(url_for("login"))
        else:
            # if insertUser returns False then notify and let them try again
            flash("This user already exists. Try again.","danger")
            return redirect(url_for("register"))

    # this is what happens when somone just visits the register
    # enpoint for the first time (before they submit something)
    return render_template("register.html", form=form)

# login page
@app.route("/login", methods=["GET", "POST"])
def login():
    # this creates an object that contains the 
    # LoginForm fields and validation rules
    form = classes.forms.LoginForm(request.form)

    # because this form submits to itself we will see if 
    # anything has been submitted and treat it differently
    # this only works if all fields have validated correctly
    if request.method == "POST" and form.validate():

        # grab user inputs from form 
        username = form.username.data
        passwordAttempt = form.password.data

        # create a user object so that we can access the 
        # user methods this comes from classes/user.py
        user = User()

        # here we call the authenticateUser method on the user class
        # it will return a boolean of False or the user's ID
        auth = user.authenticateUser(username, passwordAttempt)

        # if authentication was successful
        if auth:
            # create a user session. session comes from flask
            session['logged_in'] = True
            session['username'] = username
            session['user_id'] = auth
            #print(session['user_id'])
            # notify user and send them to their dashboard
            flash("You are now logged in, "+username+".","success")
            return redirect(url_for("home", name=username))
        
        else:
            # if authentication failed 
            error = "Incorrect username or password."
            return render_template("login.html",form=form,error=error)

    # this is what happens when somone just visits the login
    # enpoint for the first time (before they submit something)
    return render_template("login.html",form=form)

# logouts the user
@app.route("/logout")
# this will only be available to logged in users
@is_loggged_in
def logout():

    # this gets rid of the current session (logs user out)
    session.clear()

    # notify and send them to the login endpoint
    flash("You are now logged out.","success")
    return redirect(url_for("login"))

# add topic to viewed topics 
@app.route("/topicadd", methods=["GET", "POST"])
@is_loggged_in
def topic():
    # this creates an object that contains the TopicsForm fields
    # and validation rules
    form = classes.forms.TopicsForm(request.form)

    # because this form submits to itself we will see if 
    # anything has been submitted and treat it differently
    # this only works if all fields have validated correctly
    if request.method == "POST" and form.validate():

        # grab user inputs from form 
        topic = form.topic.data

        # create a user object so that we can access the user methods
        # this comes from classes/user.py
        user = User()

        # here we call the insertUser method on the user class
        # it will return message related to what has happened which is then told to the user
        success = user.insertTopic(topic, session['user_id'])

        
        if success == "new topic":
            # if topic is new inform user and make new topic and connect topic to user
            flash("You have now added the fresh topic '"+topic+"' to the topics you can view.","success")
            return redirect(url_for("topics"))
        elif success == "already in database now connected with user":
            # if topic already in database inform user it has been used before and take to topics page
            flash("You have now added the previously used topic '"+topic+"' to the topics you can view.","success")
            return redirect(url_for("topics"))
        elif success == "already connected to user":
            # if topic already connected to user inform them and take them to the topics page
            flash("This topic was already in the topics you can view. Try again.","danger")
            return redirect(url_for("topics"))
        else:
            # goes here if topic string is either not longer then 4 characters or shorter then 50 characters
            # or somehow the user makes an invalid string
            flash("This topic was invalid. Try again.","danger")
            return redirect(url_for("topic"))
    # this is what happens when somone just visits the add topic page
    # enpoint for the first time (before they submit something)
    return render_template("topicadd.html",form=form)

# deletes topic connection to user
@app.route("/topicdelete", methods=["GET", "POST"])
@is_loggged_in
def topicdelete():
    # this creates an object that contains the TopicsForm fields
    # and validation rules
    form = classes.forms.TopicsForm(request.form)

    # because this form submits to itself we will see if 
    # anything has been submitted and treat it differently
    # this only works if all fields have validated correctly
    if request.method == "POST" and form.validate():

        # grab user inputs from form 
        topic = form.topic.data

        # create a user object so that we can access the user methods
        # this comes from classes/user.py
        user = User()

        # here we call the deleteTopic method on the user class
        # it will return a boolean of either True or False
        success = user.deleteTopic(topic, session['user_id'])

        if success:
            # if user successfully deletes topic we let them know and send them to topics page
            flash("You have now deleted the topic from what you can view. You can view it again by adding "+ topic +" it again","success")
            return redirect(url_for("topics"))
        else:
            # if deleteTopic returns False then notify and send them to topics page
            flash("Topic is not in the topics you can view meaning you can't delete it. Try again.","danger")
            return redirect(url_for("topics"))
    # this is what happens when somone just visits the topic delete page
    # enpoint for the first time (before they submit something)
    return render_template("topicdelete.html",form=form)

# user topics page
@app.route("/topics")
# this will only be available to logged in users
@is_loggged_in
def topics():
    # create a sensor object so that we can access the sensor methods
    # this comes from classes/sensor.py
    sensor = Sensor()
    userTopics = sensor.retrieveUserTopics(session['user_id'])
    # checks if there is any topics connected to the user
    if userTopics:
        return render_template("topics.html", name=session['username'],topics=userTopics)
    else:
        flash("Something went wrong. No topics added exist for user: "+session['username'],"danger")
        return redirect(url_for("home"))

# sensor data related to a topic connected to the user
@app.route("/sensorData", methods=["GET", "POST"])
# this will only be available to logged in users
@is_loggged_in
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
        sensor = Sensor()
        # tries to get the sensor data related to the topic and will then tell user what happened
        userSensorData = sensor.retrieveSelectUserSensors(session['user_id'],topic)
        # checks if there is any data connected to a topic and if the topic is connected to the user
        if userSensorData == "fail":
            flash("Something went wrong. Topic: "+ topic +" added to viewed topics for user: "+session['username'],"danger")
            return redirect(url_for("home"))
        elif userSensorData:
            # gets the graph information
            df = sensor.getGraph(topic)
            # finishes setting up graph
            fig = px.line(df, x='Date Time', y='Temperature (°C)')
            # plots graph
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            # renders the graph and 20 most recent data 
            return render_template("sensorData2.html",graphJSON=graphJSON,sensorData=userSensorData,topic=topic)
        else:
            flash("There was no data assigned to topic '"+topic+"'.","danger")
            return redirect(url_for("home"))
    # this is what happens when somone just visits the add topic page
    # enpoint for the first time (before they submit something)
    return render_template("sensorData.html",form=form2)

# runs the program
app.run(debug=False)