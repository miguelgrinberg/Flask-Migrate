#!/bin/env python
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
    basedir, 'app1.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_BINDS'] = {
    "db1": "sqlite:///" + os.path.join(basedir, "app2.db"),
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


@app.cli.command()
def add():
    """Add test users."""
    db.session.add(User(name='test'))
    db.session.add(Group(name='group'))
    db.session.commit()


if __name__ == '__main__':
    app.run()
