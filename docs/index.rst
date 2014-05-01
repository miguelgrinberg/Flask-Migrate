.. Flask-Migrate documentation master file, created by
   sphinx-quickstart on Fri Jul 26 14:48:13 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Flask-Migrate's documentation!
==========================================

**Flask-Migrate** is an extension that handles SQLAlchemy database migrations for Flask applications using Alembic. The database operations are provided as command line arguments for Flask-Script.

Example
-------

This is an example application that handles database migrations through Flask-Migrate::

    from flask import Flask
    from flask.ext.sqlalchemy import SQLAlchemy
    from flask.ext.migrate import Migrate, cli as migrate_cli

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

    db = SQLAlchemy(app)
    migrate = Migrate(app, db)

    app.cli.add_command(migrate_cli, 'db')


    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(128))

With the above application you can create the database or enable migrations if the database already exists with the following command::

    $ flask --app=app db init
    
This will add a `migrations` folder to your application. The contents of this folder need to be added to version control along with your other source files. 

You can then generate an initial migration::

    $ flask --app=app db migrate
    
The migration script needs to be reviewed and edited, as Alembic currently does not detect every change you make to your models. In particular, Alembic is currently unable to detect indexes. Once finalized, the migration script also needs to be added to version control.

Then you can apply the migration to the database::

    $ flask --app=app db upgrade
    
Then each time the database models change repeat the ``migrate`` and ``upgrade`` commands.

To sync the database in another system just refresh the `migrations` folder from source control and run the ``upgrade`` command.

To see all the commands that are available run this command::

    $ flask --app=app db --help

Command Reference
-----------------

Flask-Migrate exposes two objects, ``Migrate`` and ``cli``. The former is used to initialize the extension, while the latter is a `click <http://click.pocoo.org/>`_ ``group`` instance that needs to be registered with the Flask applicatdion instance cli to expose the extension's command line options::

    from flask.ext.migrate import Migrate, cli as migrate_cli
    migrate = Migrate(app, db)
    app.cli.add_command(migrate_cli, 'db')

The two arguments to ``Migrate`` are the application instance and the Flask-SQLAlchemy database instance.

The application will now have a ``db`` command line option with several sub-commands. If your application module is called ``app`` then the commands are:

- ``flask --app=app db --help``
    Shows a list of available commands.
    
- ``flask --app=app db init``
    Initializes migration support for the application.
    
- ``flask --app=app db revision [--message MESSAGE] [--autogenerate] [--sql]``
    Creates an empty revision script. The script needs to be edited manually with the upgrade and downgrade changes. See `Alembic's documentation <https://alembic.readthedocs.org/en/latest/index.html>`_ for instructions on how to write migration scripts. An optional migration message can be included.
    
- ``flask --app=app db migrate``
    Like ``revision --autogenerate``, but the migration script is populated with changes detected automatically. The generated script should to be reviewed and edited as not all types of changes can be detected. This command does not make any changes to the database.
    
- ``flask --app=app db upgrade [--sql] [--tag TAG] [revision]``
    Upgrades the database. If ``revision`` isn't given then ``"head"`` is assumed.
    
- ``flask --app=app db downgrade [--sql] [--tag TAG] [revision]``
    Downgrades the database. If ``revision`` isn't given then ``-1`` is assumed.
    
- ``flask --app=app db stamp [--sql] [--tag TAG] [revision]``
    Sets the revision in the database to the one given as an argument, without performing any migrations.
    
- ``flask --app=app db current``
    Shows the current revision of the database.
    
- ``flask --app=app db history [--rev-range REV_RANGE]``
    Shows the list of migrations. If a range isn't given then the entire history is shown.

- ``flask --app=app db branches``
    Lists revisions that have broken the source tree into two versions representing two independent sets of changes.

Notes:
 
- All options also take a ``--directory DIRECTORY`` option that points to the directory containing the migration scripts. If this argument is omitted the directory used is `migrations`.
- The default directory can also be specified as a ``directory`` argument to the ``Migrate`` constructor.
- The ``--sql`` option present in several commands performs an 'offline' mode migration. Instead of executing the database commands the SQL statements that need to be executed are displayed.

API Reference
-------------

The commands exposed by Flask-Migrate's interface to click can also be accessed programmatically by importing the functions from module ``flask.ext.migrate``. The available functions are:

- ``init(directory='migrations')``
    Initializes migration support for the application.

- ``current(directory='migrations')``
    Shows the current revision of the database.
    
- ``revision(directory='migrations', message=None, autogenerate=False, sql=False)``
    Creates an empty revision script.

- ``migrate(directory='migrations', message=None, sql=False)``
    Creates an automatic revision script.

- ``upgrade(directory='migrations', revision='head', sql=False, tag=None)``
    Upgrades the database.

- ``downgrade(directory='migrations', revision='-1', sql=False, tag=None)``
    Downgrades the database.

- ``stamp(directory='migrations', revision='head', sql=False, tag=None)``
    Sets the revision in the database to the one given as an argument, without performing any migrations.

- ``history(directory='migrations', rev_range=None)``
    Shows the list of migrations. If a range isn't given then the entire history is shown.

Note: For greater scripting flexibility the API exposed by Alembic, on which these functions are based, can be used.
