from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '81e742d46e907b0fb07826ddf0bfb5b9'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Agrow.db'
app.config['JSON_AS_ASCII'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from flaskblog import routes
