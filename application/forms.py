from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField
from wtforms import validators
from wtforms.validators import Length, InputRequired, Email, Length

class LoginForm(FlaskForm):
    login_email = StringField("Email", validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    login_password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=80)])
    submit = SubmitField("login")

class RegisterForm(FlaskForm):
    register_username = StringField("Username", validators=[InputRequired(), Length(min=4, max=15)])
    register_email = StringField("Email", validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    register_password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=80)])
