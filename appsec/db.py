import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

currdir = os.path.dirname(__file__)
dbdir = os.path.join(currdir, 'db')

def db_file_path():
    os.path.join(dbdir, 'appsec.db')

class User(Base):
    __tablename__ = 'user'
    # Use numeric id as primary key, in case username changes in the future, and
    # integers are faster than strings when used to join on
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    # 64 bytes in a SHA512 hash; 128 characters when represented in hex
    password_hash = Column(String(128), nullable=False)
    # Assuming 16 random bytes base64 encoded into a string
    salt = Column(String(24), nullable=False)

class Session(Base):
    __tablename__ = 'session'
    # Assuming UUID4
    id = Column(String(36), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

class AuthEvent(Base):
    __tablename__ = 'authevent'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    # 0 for logout, 1 for login
    type = Column(Boolean, nullable=False)
    datetime = Column(DateTime(timezone=False), nullable=False)

class Submission(Base):
    __tablename__ = 'submission'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    text = Column(Text, nullable=False)
    result = Column(Text)

engine = create_engine(f'sqlite:///{db_file_path()}')

# Create all tables in the database
Base.metadata.create_all(engine)
