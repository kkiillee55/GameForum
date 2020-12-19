from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_cors import CORS
import os



application=Flask(__name__)
application.config['SECRET_KEY']='my secret'
application.config['SQLALCHEMY_DATABASE_URI']=os.environ.get('database')



db=SQLAlchemy(application)
bcrypt=Bcrypt(application)




application.config['MAIL_SERVER']='smtp.gmail.com'
application.config['MAIL_PORT']=587
application.config['MAIL_USE_TLS']=True
application.config['MAIL_USERNAME']=os.environ.get('email')
application.config['MAIL_PASSWORD']=os.environ.get('email_password')
mail=Mail(application)



#
from APIs.user import user
from APIs.test import test
from APIs.game import game
from APIs.index import index
from APIs.general_query import general_query
from APIs.search import search
application.register_blueprint(user,url_prefix='/api/user')
application.register_blueprint(test,url_prefix='/api/test')
application.register_blueprint(game,url_prefix='/api/game')
application.register_blueprint(index,url_prefix='/api/index')
application.register_blueprint(general_query,url_prefix='/api/general_query')
application.register_blueprint(search,url_prefix='/api/search')
CORS(application)