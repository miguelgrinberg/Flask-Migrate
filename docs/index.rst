.. Flask-Migrate documentation master file, created by
   sphinx-quickstart on Fri Jul 26 14:48:13 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Flask-Migrate's documentation!
==========================================

**Flask-Migrate** is an extension that handles SQLAlchemy database migrations for Flask applications using Alembic. The database operations are provided as command line arguments for Flask-Script.

Installation
------------

Install Flask-Migrate with `pip`:

    pip install Flask-Migrate

Example
-------

This is an example application that handles database migrations through Flask-Migrate::

    from flask import Flask
    from flask.ext.sqlalchemy import SQLAlchemy
    from flask.ext.script import Manager
    from flask.ext.migrate import Migrate, MigrateCommand

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

    db = SQLAlchemy(app)
    migrate = Migrate(app, db)

    manager = Manager(app)
    manager.add_command('db', MigrateCommand)

    class User(db.Model):
        id = db.Column(db.Integer, primary_key = True)
        name = db.Column(db.String(128))

    if __name__ == '__main__':
        manager.run()

With the above application you can create the database or enable migrations if the database already exists with the following command::

    $ python app.py db init
    
This will add a `migrations` folder to your application. The contents of this folder need to be added to version control along with your other source files. 

You can then generate an initial migration::

    $ python app.py db migrate
    
The migration script needs to be reviewed and edited, as Alembic currently does not detect every change you make to your models. In particular, Alembic is currently unable to detect indexes. Once finalized, the migration script also needs to be added to version control.

Then you can apply the migration to the database::

    $ python app.py db upgrade
    
Then each time the database models change repeat the ``migrate`` and ``upgrade`` commands.

To sync the database in another system just refresh the `migrations` folder from source control and run the ``upgrade`` command.

To see all the commands that are available run this command::

    $ python app.py db --help

Command Reference
-----------------

Flask-Migrate exposes two objects, ``Migrate`` and ``MigrateCommand``. The former is used to initialize the extension, while the latter is a ``Manager`` instance that needs to be registered with Flask-Script to expose the extension's command line options::

    from flask.ext.migrate import Migrate, MigrateCommand
    migrate = Migrate(app, db)
    manager.add_command('db', MigrateCommand)

The two arguments to ``Migrate`` are the application instance and the Flask-SQLAlchemy database instance.

The application will now have a ``db`` command line option with several sub-commands. If your launch script is called ``manage.py`` then the commands are:

- ``manage.py db --help``
    Shows a list of available commands.
    
- ``manage.py db init``
    Initializes migration support for the application.
    
- ``manage.py db revision [--message MESSAGE] [--autogenerate] [--sql]``
    Creates an empty revision script. The script needs to be edited manually with the upgrade and downgrade changes. See `Alembic's documentation <https://alembic.readthedocs.org/en/latest/index.html>`_ for instructions on how to write migration scripts. An optional migration message can be included.
    
- ``manage.py db migrate``
    Like ``revision --autogenerate``, but the migration script is populated with changes detected automatically. The generated script should to be reviewed and edited as not all types of changes can be detected. This command does not make any changes to the database.
    
- ``manage.py db upgrade [--sql] [--tag TAG] [revision]``
    Upgrades the database. If ``revision`` isn't given then ``"head"`` is assumed.
    
- ``manage.py db downgrade [--sql] [--tag TAG] [revision]``
    Downgrades the database. If ``revision`` isn't given then ``-1`` is assumed.
    
- ``manage.py db stamp [--sql] [--tag TAG] [revision]``
    Sets the revision in the database to the one given as an argument, without performing any migrations.
    
- ``manage.py db current``
    Shows the current revision of the database.
    
- ``manage.py db history [--rev-range REV_RANGE]``
    Shows the list of migrations. If a range isn't given then the entire history is shown.

- ``manage.py db branches``
    Lists revisions that have broken the source tree into two versions representing two independent sets of changes.

Notes:
 
- All options also take a ``--directory DIRECTORY`` option that points to the directory containing the migration scripts. If this argument is omitted the directory used is `migrations`.
- The default directory can also be specified as a ``directory`` argument to the ``Migrate`` constructor.
- The ``--sql`` option present in several commands performs an 'offline' mode migration. Instead of executing the database commands the SQL statements that need to be executed are displayed.

API Reference
-------------

The commands exposed by Flask-Migrate's interface to Flask-Script can also be accessed programmatically by importing the functions from module ``flask.ext.migrate``. The available functions are:

- ``init(directory = 'migrations')``
    Initializes migration support for the application.

- ``current(directory = 'migrations')``
    Shows the current revision of the database.
    
- ``revision(directory = 'migrations', message = None, autogenerate = False, sql = False)``
    Creates an empty revision script.

- ``migrate(directory = 'migrations', message = None, sql = False)``
    Creates an automatic revision script.

- ``upgrade(directory = 'migrations', revision = 'head', sql = False, tag = None)``
    Upgrades the database.

- ``downgrade(directory = 'migrations', revision = '-1', sql = False, tag = None)``
    Downgrades the database.

- ``stamp(directory = 'migrations', revision = 'head', sql = False, tag = None)``
    Sets the revision in the database to the one given as an argument, without performing any migrations.

- ``history(directory = 'migrations', rev_range = None)``
    Shows the list of migrations. If a range isn't given then the entire history is shown.

Note: For greater scripting flexibility the API exposed by Alembic, on which these functions are based, can be used.
