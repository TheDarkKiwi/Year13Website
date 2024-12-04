# import needed modules
import sqlite3
from config import Config
import datetime
import pandas as pd

# create a config object so we can access it's properties
config = Config()


class Sensor:

    # this is a contructor class
    # it holds properties of the object that can be 
    # referred to throughout via "self"
    def __init__(self):
        # path is relative to root of app (app.py)
        # it comes from the config.py class in the root folder
        self.dbPath = config.dbName




    # this method gets all sensor data(not used anymore)
    def retrieveAllSensor(self):

        with sqlite3.connect(self.dbPath) as con:

            # this makes the results come back as a dictionary
            con.row_factory = sqlite3.Row 
            # create cursor
            cur = con.cursor()
            # SQL statement get all sensor data
            cur.execute("SELECT * FROM sensorData")
            # get the results
            result = cur.fetchall()
            # close our connection
            cur.close()

            # if the result exists then return it to app.py else return False
            if result:
                return result
            else:
                return False

    # this method retrieves just the users sensor data
    # (not used any more but have left in incase I ever might need it)
    def retrieveAllUserSensors(self,id_user):

        with sqlite3.connect(self.dbPath) as con:
 
            # this makes the results come back as a dictionary
            con.row_factory = sqlite3.Row 
            # create cursor
            cur = con.cursor()
            # SQL statement finding all sensor data related to a user with sort by descending order
            cur.execute("""SELECT sensorData.temperature, sensorData.currentdate, 
            sensorData.currenttime, topics.topic FROM sensorData 
            JOIN topics ON sensorData.fromTopic = topics.id, users_topics ON 
            topics.id = users_topics.id_topics, users ON users_topics.id_users = users.id 
            WHERE users_topics.id_users = ? 
            ORDER BY sensorData.id DESC LIMIT 20""",[id_user])
            # get the results
            result = cur.fetchall()
            # close our connection
            cur.close()

            # if the result exists then return it to app.py else return False
            if result:
                return result
            else:
                return False

    def retrieveSelectUserSensors(self,id_user,topic):

        with sqlite3.connect(self.dbPath) as con:
            # this makes the results come back as a dictionary
            con.row_factory = sqlite3.Row 
            cur = con.cursor()
            # SQL statement to find if a topic is connected to the user
            cur.execute("""SELECT * FROM users_topics
            JOIN topics ON users_topics.id_topics = topics.id
            WHERE topics.topic = ? AND users_topics.id_users = ?""",[topic,id_user])
            # get the results
            result2 = cur.fetchone()
            # close our connection
            cur.close()
            #print(result2)
            #if the topic is connected to the user checks if there is data related to it
            if result2:
                # create cursor
                cur = con.cursor()
                # SQL statement finding topic sensor data sorted by descending order up to 20 most recent
                cur.execute("""SELECT sensorData.temperature, sensorData.currentdate, 
                sensorData.currenttime FROM sensorData 
                JOIN topics ON sensorData.fromTopic = topics.id
                WHERE topics.topic = ? 
                ORDER BY sensorData.id DESC LIMIT 20""",[topic])
                # get the results
                result = cur.fetchall()
                # close our connection
                cur.close()
                #if there is a result return it to app.py else return false
                if result:
                    return result
                else:
                    return False
            else:
                return "fail"
    
    # this method retrieves just the users topics
    def retrieveUserTopics(self,id_user):

        with sqlite3.connect(self.dbPath) as con:
 
            # this makes the results come back as a dictionary
            con.row_factory = sqlite3.Row 
            # create cursor
            cur = con.cursor()
            # SQL statement finding all users topics
            cur.execute("SELECT topics.id, topics.topic FROM topics JOIN users_topics ON topics.id = users_topics.id_topics, users ON users_topics.id_users = users.id WHERE users_topics.id_users = ?",[id_user])
            # get the results
            result = cur.fetchall()
            # close our connection
            cur.close()

            # if the result exists then return it to app.py else return False
            if result:
                return result
            else:
                return False
    # gets graph data so can be formated a a graph
    def getGraph(self,topic):
        with sqlite3.connect(self.dbPath) as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # gets al data for a topic
            cur.execute("""SELECT sensorData.temperature, sensorData.currentDateTime FROM sensorData 
               JOIN topics ON sensorData.fromTopic = topics.id
               WHERE topics.topic = ?""",[topic])
            # get the results
            data = cur.fetchall()

            # close our connection
            cur.close()
            # sets all the data points for a graph
            df = pd.DataFrame( [[ij for ij in i] for i in data] )
            # renames the columns so axis names are better and say what they mean in plain text
            df.rename(columns={0: 'Temperature (°C)', 1: 'Date Time'}, inplace=True)
            # sorts the data by date
            df = df.sort_values(['Date Time'], ascending=[1])
            # returns the data to be graphed
            return df