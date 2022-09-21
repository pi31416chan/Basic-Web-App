# Imports
from flask_sqlalchemy import SQLAlchemy



# Extension Initialization
db = SQLAlchemy()



# DB Class Definition
class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(30),unique=True,nullable=False)
    email = db.Column(db.String(50),unique=True,nullable=False)
    password_hash = db.Column(db.String(102),unique=True,nullable=False)
    
    def __repr__(self) -> str:
        return f"< User '{self.email}'>"

class APIKey(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    key = db.Column(db.String(40),unique=True,nullable=False)
    device_name = db.Column(db.String(50),unique=True,nullable=False)
    active = db.Column(db.Boolean,nullable=False,default=True)