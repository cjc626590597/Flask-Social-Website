from datetime import timedelta
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect
from flask_socketio import SocketIO

app = Flask(__name__, static_folder="static")
app.config['SECRET_KEY'] = 'f8ee4cbd64785576bab7b14bc37747640c6a4837cf6cd0c5'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://c1985846:Groupproject4@csmysql.cs.cf.ac.uk:3306/c1985846_Group4_Y2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:a123456@localhost:3306/c1985846_Group4_Y2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CsrfProtect(app)
socketio = SocketIO()

db = SQLAlchemy(app, session_options={"autoflush": False, "autocommit": False})

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
socketio.init_app(app)

from website import routes
