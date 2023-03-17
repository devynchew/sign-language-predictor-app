from flask import Flask
from flask_login import LoginManager
from keras.models import load_model
from flask_cors import CORS

# For persistent storage
from flask_sqlalchemy import SQLAlchemy

#create the Flask app
app = Flask(__name__)
CORS(app)

# load configuration from config.cfg
app.config.from_pyfile('config.cfg')

# instantiate SQLAlchemy to handle db process
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# AI model file
model_file = "./application/static/sign_language_model.h5"

# Load from file
ai_model = load_model(model_file)

# set upload folder
UPLOAD_FOLDER = './application/static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# run the file routes.py
from application import routes


