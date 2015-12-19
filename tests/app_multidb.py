#!/bin/env python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app1.db'
app.config['SQLALCHEMY_BINDS'] = {
    "db1": "sqlite:///app2.db",
}

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))


class Group(db.Model):
    __bind_key__ = 'db1'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', migrate.make_command())


if __name__ == '__main__':
    manager.run()
