from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type=True)

manager = Manager(app)
manager.add_command('db', migrate.make_command())


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))

if __name__ == '__main__':
    manager.run()
