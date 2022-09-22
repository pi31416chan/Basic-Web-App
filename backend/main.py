# Imports
import os
from flask import (
    Flask
)
from package import (
    api,
    db
)



# Flask App Initialization
app = Flask(__name__)

# Setting default config
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['TOKEN_SECRET_KEY'] = os.environ.get('TOKEN_SECRET_KEY')
app.config['TOKEN_EXPIRY'] = int(os.environ.get('TOKEN_EXPIRY'))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///./database/dev.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Extension Initialization
api.init_app(app)
db.init_app(app)

# Create the database tables if not found
with app.app_context():
    db.create_all()

print()