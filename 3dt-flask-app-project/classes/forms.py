# import the Flask-WTF library
from wtforms import Form, validators, StringField, PasswordField


# ---------------------------------------------

# This class defines the registration form:
# - fields that it needs
# - validation rules for each field
class RegisterForm(Form):

    # The Flask-WTF system uses this syntax. By using this system,
    # we save a lot of time coding validation rules for each field.
    # Length defines the min and max acceptable number of characters 
    # for each field. For example, a username needs to be at least 4 
    # characters long and no longer than 15 characters.
    # DataRequired() tells Flask that they need to have entered something
    # or it will send them an error message.
    username = StringField("Username",[validators.Length(min=4,max=15)])
    email = StringField("Email",[validators.Length(min=6,max=50)])
    password = PasswordField("Password",[validators.DataRequired()])
    confirm = PasswordField("Confirm Password", [validators.DataRequired(),validators.EqualTo("password", message="Passwords do not match.")])

# ---------------------------------------------


# This class defines the login form:
# - fields that it needs
# - validation rules for each field
class LoginForm(Form):

    # this is almost the same as for the registration form above.
    username = StringField("Username",[validators.Length(min=4,max=15),validators.DataRequired()])
    password = PasswordField("Password",[validators.DataRequired()])

# ---------------------------------------------

# this class creates a form so that logged in users can add topics to the topics the can view or 
# delete them from thier viewed topics
class TopicsForm(Form):
    topic = StringField("Topic",[validators.Length(min=4,max=50),validators.DataRequired()])