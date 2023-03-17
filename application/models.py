from numpy.lib.arraysetops import unique
from application import db, login_manager
from flask_login import UserMixin
import datetime as dt

# prediction table
class Entry(db.Model):
    __tablename__ = 'sign_language_predictions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer)
    filename = db.Column(db.String)
    filepath = db.Column(db.String)
    prediction = db.Column(db.String)
    predicted_on = db.Column(db.DateTime, nullable=False)

# user data table
class UserData(UserMixin, db.Model):
    __bind_key__ = 'usersdata'
    __tablename__ = 'usersdata'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(15),unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return UserData.query.get(int(user_id))