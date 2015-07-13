from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_BINDS'] = {
    "db1": "sqlite:///app1.db",
}

db = SQLAlchemy(app)
migrate = Migrate(app, db)
db1 = SQLAlchemy(app)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

metadata = db.metadata
metadata1 = db1.metadata


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))


class Group(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    name = db1.Column(db1.String(128))


if __name__ == '__main__':
    manager.run()
