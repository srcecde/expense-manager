from flask import Flask
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# engine = create_engine('postgresql://postgres:root@localhost:5432/', convert_unicode=True)

# conn = engine.connect()
# conn.connection.connection.set_isolation_level(0)

# try:
#     conn.execute('create database expmanager')
# except:
#     pass
# conn.connection.connection.set_isolation_level(1)
# db_session = scoped_session(sessionmaker(autocommit=False,
#                                          autoflush=False,
#                                          bind=engine))

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/expmanager'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class users(db.Model):
    __tablename__ = 'users'
    uid = db.Column('uid', db.Integer, primary_key=True)
    username = db.Column('username', db.String(20))
    password = db.Column('password', db.String(255))
    email = db.Column('email', db.String(50))

    def __init__(self, uid, username, password, email):
        self.uid = uid
        self.username = username
        self.password = password
        self.email = email


class Category(db.Model):
    __tablename__ = 'category'
    cid = db.Column('cid', db.Integer, primary_key=True)
    uid_fk = db.Column('uid_fk', db.Integer, db.ForeignKey(users.uid))
    categories = db.Column('categories', db.String(100))

    def __init__(self, cid, uid_fk, categories):
        self.cid = cid
        self.uid_fk = uid_fk
        self.categories = categories


class Budget(db.Model):
    __tablename__ = 'budget'
    bid = db.Column('bid', db.Integer, primary_key=True)
    uid_fk = db.Column('uid_fk', db.Integer, db.ForeignKey('users.uid'))
    bdate = db.Column('bdate', db.Date)
    monthly_budget = db.Column('monthly_budget', db.Integer)

    def __init__(self, bid, uid_fk, bdate, monthly_budget):
        self.bid = bid
        self.uid_fk = uid_fk
        self.bdate = bdate
        self.monthly_budget = monthly_budget


class Expense(db.Model):
    __tablename__ = 'expense'
    eid = db.Column('eid', db.Integer, primary_key=True)
    uid_fk = db.Column('uid_fk', db.Integer, db.ForeignKey('users.uid'))
    cid_fk = db.Column('cid_fk', db.Integer, db.ForeignKey('category.cid'))
    date = db.Column('date', db.Date)
    amount = db.Column('amount', db.Integer)
    description = db.Column('description', db.String(200))


    def __init__(self, eid, uid_fk, cid_fk, date, amount, description):
        self.eid = eid
        self.uid_fk = uid_fk
        self.cid_fk = cid_fk
        self.date = date
        self.amount = amount
        self.description = description


class Box12(db.Model):
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Date, unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email
