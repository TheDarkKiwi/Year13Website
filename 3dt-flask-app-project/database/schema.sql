CREATE TABLE 'users_topics' (
'id' INTEGER DEFAULT NULL PRIMARY KEY AUTOINCREMENT,
'id_users' INTEGER DEFAULT NULL REFERENCES 'users' ('id'),
'id_topics' INTEGER DEFAULT NULL REFERENCES 'topics' ('id')
);

CREATE TABLE 'topics' (
'id' INTEGER DEFAULT NULL PRIMARY KEY AUTOINCREMENT,
'topic' TEXT DEFAULT NULL
);

CREATE TABLE 'users' (
'id' INTEGER DEFAULT NULL PRIMARY KEY AUTOINCREMENT,
'username' TEXT DEFAULT NULL,
'email' TEXT DEFAULT NULL,
'password' TEXT DEFAULT NULL
);

CREATE TABLE 'sensorData' (
'id' INTEGER DEFAULT NULL PRIMARY KEY AUTOINCREMENT,
'fromTopic' INTEGER DEFAULT NULL REFERENCES 'topics' ('id'),
'temperature' NUMERIC DEFAULT NULL,
'currentdate' DATE DEFAULT NULL,
'currenttime' TIME DEFAULT NULL,
'currentDateTime' DATETIME Default NULL
);