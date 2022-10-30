# Imports
import os
from flask_bootstrap import Bootstrap5
from flask import (
    Flask
)
from flask_session import Session
from modules import (
    login,
    register,
    logout,
    home,
    change_password
)



# Flask App Initialization
app = Flask(__name__)

# Setting default config
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['API_KEY'] = os.environ.get('API_KEY')
app.config['SESSION_TYPE'] = 'filesystem'

# Extension Initialization
bootstrap = Bootstrap5(app)
Session(app)



# Routing
app.add_url_rule('/login',view_func=login,methods=['GET','POST'])
app.add_url_rule('/logout',view_func=logout,methods=['GET'])
app.add_url_rule('/register',view_func=register,methods=['GET','POST'])
app.add_url_rule('/','home',view_func=home)
app.add_url_rule('/home','home',view_func=home)
app.add_url_rule('/change_password','change_password',view_func=change_password,methods=['GET','POST'])
