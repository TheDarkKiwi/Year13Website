"""
This script creates the sqlite3 database according to the schema.sql file in the same directory.

"""

import sqlite3

# the name of the database must match the one in the config file
# although the one in the config is a path/filename.db
con = sqlite3.connect("database/database.db")

# your database schema must live in the schema.sql file in this directory
with open("database/schema.sql") as schema:
    con.executescript(schema.read())