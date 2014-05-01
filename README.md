Flask-Migrate
=============

[![Build Status](https://travis-ci.org/miguelgrinberg/Flask-Migrate.png?branch=master)](https://travis-ci.org/miguelgrinberg/Flask-Migrate)

Flask-Migrate is an extension that handles SQLAlchemy database migrations for Flask applications using Alembic. The database operations are provided as command line arguments for Flask-Script.

Example
-------

This is an example application that handles database migrations through Flask-Migrate:

    from flask import Flask
    from flask.ext.sqlalchemy import SQLAlchemy
    from flask.ext.migrate import Migrate, cli as migrate_cli

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

    db = SQLAlchemy(app)
    migrate = Migrate(app, db)

    app.cli.add_command(migrate_cli, 'db')


    class User(db.Model):
        id = db.Column(db.Integer, primary_key = True)
        name = db.Column(db.String(128))

With the above application you can create the database or enable migrations if the database already exists with the following command:

    $ flask --app=app db init
    
This will add a `migrations` folder to your application. The contents of this folder need to be added to version control along with your other source files. 

You can then generate an initial migration:

    $ flask --app=app db migrate
    
The migration script needs to be reviewed and edited, as Alembic currently does not detect every change you make to your models. In particular, Alembic is currently unable to detect indexes. Once finalized, the migration script also needs to be added to version control.

Then you can apply the migration to the database:

    $ flask --app=app db upgrade
    
Then each time the database models change repeat the `migrate` and `upgrade` commands.

To sync the database in another system just refresh the `migrations` folder from source control and run the `upgrade` command.

To see all the commands that are available run this command:

    $ flask --app=app db --help

Resources
---------

- [Documentation](http://pythonhosted.org/Flask-Migrate)
- [pypi](https://pypi.python.org/pypi/Flask-Migrate) 
