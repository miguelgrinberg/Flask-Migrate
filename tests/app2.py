from flask import Flask
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app2.db'

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Model = declarative_base()
Model.query = db_session.query_property()
migrate = Migrate(app, Model.metadata, directory='temp_folder/temp_migrations')

manager = Manager(app)
manager.add_command('db', MigrateCommand)


class User(Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(128))

if __name__ == '__main__':
    manager.run()
