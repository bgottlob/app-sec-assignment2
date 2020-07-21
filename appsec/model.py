import pathlib
import os
import sys
from sqlalchemy import (
    Column, ForeignKey, Integer, String, Boolean, DateTime, Text,
    create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from appsec import db

currdir = os.path.dirname(__file__)
dbdir = os.path.join(currdir, 'db')
pathlib.Path(dbdir).mkdir(exist_ok=True)

def db_file_path():
    return os.path.join(dbdir, 'appsec.db')

def create_db_engine():
    return create_engine(f'sqlite:///{db_file_path()}')

def create_session():
    return sessionmaker(bind=create_db_engine())()

def clear():
    if os.path.exists(db_file_path()):
        os.remove(db_file_path())

class User(db.Model):
    __tablename__ = 'user'
    # Use numeric id as primary key, in case username changes in the future, and
    # integers are faster than strings when used to join on
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    # 64 bytes in a SHA512 hash; 128 characters when represented in hex
    password_hash = db.Column(db.String(128), nullable=False)
    # Assuming 16 random bytes base64 encoded into a string
    salt = db.Column(db.String(24), nullable=False)
    mfa = db.Column(db.String(11), nullable=False)

class AuthSession(db.Model):
    __tablename__ = 'authsession'
    # Assuming UUID4
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)

class AuthEvent(db.Model):
    __tablename__ = 'authevent'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    # 0 for logout, 1 for login
    type = db.Column(db.Boolean, nullable=False)
    datetime = db.Column(db.DateTime(timezone=False), nullable=False)

class Submission(db.Model):
    __tablename__ = 'submission'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    result = db.Column(db.Text)
