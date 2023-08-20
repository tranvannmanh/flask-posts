from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from uuid import uuid4
from . import database
from datetime import datetime

Base = declarative_base()
db = database.db

def get_uuid():
    return uuid4().hex

class User(db.Model):
    __tablename__ = "USERS"
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    fname = Column(String(50), nullable=False)
    username = Column(String(20), unique=True)
    password = Column(String(20), nullable=False)

    def __init__(self, fname=None, username=None, password=None):
        self.fname = fname
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username
    

class Category(db.Model):
    __tablename__ = "CATEGORY"
    id = Column(Integer, autoincrement=True, unique=True)
    type = Column(String(50), primary_key=True)
    name = Column(String(50), nullable=False)
    image = Column(Text, nullable=True)

class Posts(db.Model):
    __tablename__ = "NEWS"
    id = Column(Integer, autoincrement=True, unique=True, primary_key=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    created = Column(DateTime, default=datetime.now())
    author = Column(String(100), nullable=True)
    image = Column(String(345), nullable=True)
    type = Column(String(50), nullable=False)

class Recommend(db.Model):
    __tablename__="RECOMMEND"
    id = Column(Integer, autoincrement=True, primary_key=True)
    from_post_id=Column(Integer, nullable=True)
    user_id=Column(Integer, nullable=False)
    post_id=Column(Integer, nullable=False)

class YouLike(db.Model):
    __tablename__="YOU_LIKE"
    id=Column(Integer, autoincrement=True, primary_key=True)
    user_id=Column(Integer, nullable=False)
    post_id=Column(Integer, nullable=False)

class History(db.Model):
    __tablename__='HISTORY'
    id=Column(Integer, autoincrement=True, primary_key=True)
    readAt=Column(DateTime, nullable=False)
    user_id=Column(Integer, nullable=False)
    post_id=Column(Integer, nullable=False)




# recommended = db.Table('RECOMMENDED',
#                        Column('user_id', Integer, ForeignKey("USERS.id"), primary_key=True),
#                        Column('post_id', Integer, ForeignKey("NEWS.id"), primary_key=True)
#                        )
