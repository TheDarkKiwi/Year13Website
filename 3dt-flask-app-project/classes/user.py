# import needed modules
import sqlite3
from config import Config
from passlib.hash import sha256_crypt

# create a config object so we can access it's properties
config = Config()

class User:

    # this is a contructor class
    # it holds properties of the object that can be 
    # referred to throughout via "self"
    def __init__(self):
        # path is relative to root of app (app.py)
        # it comes from the config.py class in the root folder
        self.dbPath = config.dbName

    # this method inserts a new user
    def insertUser(self,username,password,email):

        # this is a convenient way to open and close 
        # a database connection. Notice how we've used the self.dbPath
        # property of the user object
        with sqlite3.connect(self.dbPath) as con:

            # creates a cursor (pointer) for our database queries
            cur = con.cursor()
            # executes some SQL to select the user's details
            cur.execute("SELECT * FROM users WHERE username = ?",[username])
            # retrieves this row from the dictionary and assigns the 
            # result to the variable result
            result = cur.fetchone()

            # if the result has returned as True, it means that 
            # the user already exists in the database so we return 
            # False to app.py where this method was called 
            if result:
                return False
            else:
                # if the user doesn't already exist in the database
                # we encrypt the password they've submitted using 
                # the sha256_crypt library
                passwordHashed = sha256_crypt.encrypt(str(password))

                # create cursor
                cur = con.cursor()
                # insert new user into database
                cur.execute("INSERT INTO users (username,password,email) VALUES (?,?,?)",[username,passwordHashed,email])
                # this commits the row in to the users table
                con.commit()
                cur.close()
                # now we return True to app.py
                return True

    # this method authenticates the user. 
    def authenticateUser(self,username,passwordAttempt):

        # open and close a database connection
        with sqlite3.connect(self.dbPath) as con:

            # Make the result a dictionary.
            con.row_factory = sqlite3.Row
            # create database cursor
            cur = con.cursor()
            # execute SQL that selects the user's details
            cur.execute("SELECT * FROM users WHERE username = ?",[username])
            # assigns the results to the result variable
            result = cur.fetchone()
            cur.close()
            
            # If we actually found a user with the name submitted
            if result:
                # get the stored hashed password from the db query above
                # since it's a dictionary we can just access the column name
                # as a key. In this case 'password'
                passwordHash = result['password']

                # This convenient method checks that the encrytped password
                # that we have stored in the database for that user matches
                # an encrypted version of what they've just attempted to log in with
                # If it matches we return the user's ID , if not we return False.
                if sha256_crypt.verify(passwordAttempt, passwordHash):
                    return result['id']
                else:
                    return False
            else:
                # this else statement is a fallback if the username
                # that was submitted isn't found in the user table in the database
                return False
    
    def insertTopic(self,topic,user_id):
        # open the database
        with sqlite3.connect(self.dbPath) as con:

            # creates a cursor (pointer) for our database queries
            cur = con.cursor()
            # executes some SQL to select the user's details
            cur.execute("SELECT * FROM topics WHERE topic = ?",[topic])
            # retrieves this row from the dictionary and assigns the 
            # result to the variable result
            result = cur.fetchone()

            # if the result has returned as True, it means that 
            # the topic already exists in the database so we 
            # find if it already connected to the user or not
            if result:
                # get the id of the topic
                topic_id = result[0]
                # checks if the topic is already related to the user
                cur.execute("SELECT * FROM users_topics WHERE users_topics.id_topics = ? AND users_topics.id_users = ?",[topic_id,user_id])
                # sets result to result2 to make sure no previous databse 
                # searches data messes with the if statement
                result2 = cur.fetchone()
                # if result return "already connected to user"
                # overwise connect it and tell the user it isn't a fresh database
                if result2:
                    return "already connected to user"
                else:
                    cur.execute("INSERT INTO users_topics (id_users, id_topics) VALUES (?,?)",[user_id,topic_id])
                    # this commits the row in to the users_topics table
                    con.commit()
                    cur.close()
                    # now we return True to app.py so that we can handle errors/success
                    return "already in database now connected with user"
            else:
                # insert a new topic into the database
                #print(topic)
                cur.execute("INSERT INTO topics (topic) VALUES (?)",[topic])
                topic_id = cur.lastrowid
                cur.execute("INSERT INTO users_topics (id_users, id_topics) VALUES (?,?)",[user_id,topic_id])
                # this commits the row in ot he users_topics table
                con.commit()
                cur.close()
                # now we return True to app.py so that we can handle errors/success
                return "new topic"

    def deleteTopic(self,topic,user_id):
        # open the database
        with sqlite3.connect(self.dbPath) as con:
            
            cur = con.cursor()
            # executes some SQL to select the see if the user is connected to a topic
            cur.execute("""SELECT * FROM topics JOIN users_topics ON 
            topics.id = users_topics.id_topics WHERE topic = ? AND users_topics.id_users = ?""",[topic,user_id])
            # retrieves this row from the dictionary and assigns the 
            # result to the variable result
            result = cur.fetchone()

            # if the result has returned as True, it means that 
            # the user already exists in the database so we return 
            # False to app.py where this method was called 
            if result:
                topic_id = result[0]
                # deletes the connection between the user and topic
                cur.execute("DELETE FROM users_topics WHERE users_topics.id_topics = ? AND users_topics.id_users = ?",[topic_id,user_id])
                # this commits the delete into the users_topics table
                con.commit()
                cur.close()
                # now we return True to app.py so that we can handle errors/success
                return True
            else:
                return False