.. Flask-Migrate documentation master file, created by
   sphinx-quickstart on Fri Jul 26 14:48:13 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Flask-Migrate
=============

**Flask-Migrate** is an extension that handles SQLAlchemy database migrations for Flask applications using Alembic. The database operations are made available through the Flask command-line interface or through the Flask-Script extension.

Why Use Flask-Migrate vs. Alembic Directly?
-------------------------------------------

Flask-Migrate is an extension that configures Alembic in the proper way to work with your Flask and Flask-SQLAlchemy application. In terms of the actual database migrations, everything is handled by Alembic so you get exactly the same functionality.

Installation
------------

Install Flask-Migrate with `pip`::

    pip install Flask-Migrate

Example
-------

This is an example application that handles database migrations through Flask-Migrate::

    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from flask_migrate import Migrate

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

    db = SQLAlchemy(app)
    migrate = Migrate(app, db)

    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(128))

With the above application you can create a migration repository with the following command::

    $ flask db init

This will add a `migrations` folder to your application. The contents of this folder need to be added to version control along with your other source files.

You can then generate an initial migration::

    $ flask db migrate
    
The migration script needs to be reviewed and edited, as Alembic currently does not detect every change you make to your models. In particular, Alembic is currently unable to detect table name changes, column name changes, or anonymously named constraints. A detailed summary of limitations can be found in the `Alembic autogenerate documentation <http://alembic.zzzcomputing.com/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect>`_. Once finalized, the migration script also needs to be added to version control.

Then you can apply the migration to the database::

    $ flask db upgrade
    
Then each time the database models change repeat the ``migrate`` and ``upgrade`` commands.

To sync the database in another system just refresh the `migrations` folder from source control and run the ``upgrade`` command.

To see all the commands that are available run this command::

    $ flask db --help

Note that the application script must be set in the ``FLASK_APP`` environment variable for all the above commands to work, as required by the ``flask`` command line script.

Using Flask-Script
------------------

Flask-Migrate also supports the Flask-Script command-line interface. This is an example application that exposes all the database migration commands through Flask-Script::

    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from flask_script import Manager
    from flask_migrate import Migrate, MigrateCommand

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

    db = SQLAlchemy(app)
    migrate = Migrate(app, db)

    manager = Manager(app)
    manager.add_command('db', MigrateCommand)

    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(128))

    if __name__ == '__main__':
        manager.run()

Assuming the above script is stored in a file named ``manage.py``, all the database migration commands can be accessed by running the script::

    $ python manage.py db init
    $ python manage.py db migrate
    $ python manage.py db upgrade
    $ python manage.py db --help

Configuration Callbacks
-----------------------

Sometimes applications need to dynamically insert their own settings into the Alembic configuration. A function decorated with the ``configure`` callback will be invoked after the configuration is read, and before it is used. The function can modify the configuration object, or replace it with a different one.

::

    @migrate.configure
    def configure_alembic(config):
        # modify config object
        return config

Multiple configuration callbacks can be defined simply by decorating multiple functions. The order in which multiple callbacks are invoked is undetermined.

Multiple Database Support
-------------------------

Flask-Migrate can integrate with the  `binds <http://flask-sqlalchemy.pocoo.org/binds/>`_ feature of Flask-SQLAlchemy, making it possible to track migrations to multiple databases associated with an application.

To create a multiple database migration repository, add the ``--multidb`` argument to the ``init`` command::

    $ flask db init --multidb

With this command, the migration repository will be set up to track migrations on your main database, and on any additional databases defined in the ``SQLALCHEMY_BINDS`` configuration option.

Command Reference
-----------------

Flask-Migrate exposes two classes, ``Migrate`` and ``MigrateCommand``. The ``Migrate`` class contains all the functionality of the extension. The ``MigrateCommand`` class is only used when it is desired to expose database migration commands through the Flask-Script extension.

The following example initializes the extension with the standard Flask command-line interface::

    from flask_migrate import Migrate
    migrate = Migrate(app, db)

The two arguments to ``Migrate`` are the application instance and the Flask-SQLAlchemy database instance. The ``Migrate`` constructor also takes additional keyword arguments, which are passed to Alembic's ``EnvironmentContext.configure()`` method. As is standard for all Flask extensions, Flask-Migrate can be initialized using the ``init_app`` method as well::

    from flask_sqlalchemy import SQLAlchemy
    from flask_migrate import Migrate

    db = SQLAlchemy()
    migrate = Migrate()

    def create_app():
         """Application-factory pattern"""
         ...
         ...
         db.init_app(app)
         migrate.init_app(app, db)
         ...
         ...
         return app

When using Flask-Script's command-line interface, the extension is initialized as follows::

    from flask_migrate import Migrate, MigrateCommand
    migrate = Migrate(app, db)
    manager.add_command('db', MigrateCommand)

After the extension is initialized, a ``db`` group will be added to the command-line options with several sub-commands, both in the ``flask`` command or with a ``manage.py`` type script created with Flask-Script. Below is a list of the available sub-commands:

- ``flask db --help``
    Shows a list of available commands.
    
- ``flask db init [--multidb]``
    Initializes migration support for the application. The optional ``--multidb`` enables migrations for multiple databases configured as `Flask-SQLAlchemy binds <http://flask-sqlalchemy.pocoo.org/binds/>`_.
    
- ``flask db revision [--message MESSAGE] [--autogenerate] [--sql] [--head HEAD] [--splice] [--branch-label BRANCH_LABEL] [--version-path VERSION_PATH] [--rev-id REV_ID]``
    Creates an empty revision script. The script needs to be edited manually with the upgrade and downgrade changes. See `Alembic's documentation <http://alembic.zzzcomputing.com/en/latest/index.html>`_ for instructions on how to write migration scripts. An optional migration message can be included.
    
- ``flask db migrate [--message MESSAGE] [--sql] [--head HEAD] [--splice] [--branch-label BRANCH_LABEL] [--version-path VERSION_PATH] [--rev-id REV_ID]``
    Equivalent to ``revision --autogenerate``. The migration script is populated with changes detected automatically. The generated script should to be reviewed and edited as not all types of changes can be detected automatically. This command does not make any changes to the database, just creates the revision script.

- ``flask db edit <revision>``
    Edit a revision script using $EDITOR.

- ``flask db upgrade [--sql] [--tag TAG] [--x-arg ARG] <revision>``
    Upgrades the database. If ``revision`` isn't given then ``"head"`` is assumed.
    
- ``flask db downgrade [--sql] [--tag TAG] [--x-arg ARG] <revision>``
    Downgrades the database. If ``revision`` isn't given then ``-1`` is assumed.
    
- ``flask db stamp [--sql] [--tag TAG] <revision>``
    Sets the revision in the database to the one given as an argument, without performing any migrations.
    
- ``flask db current [--verbose]``
    Shows the current revision of the database.
    
- ``flask db history [--rev-range REV_RANGE] [--verbose]``
    Shows the list of migrations. If a range isn't given then the entire history is shown.

- ``flask db show <revision>``
    Show the revision denoted by the given symbol.

- ``flask db merge [--message MESSAGE] [--branch-label BRANCH_LABEL] [--rev-id REV_ID] <revisions>``
    Merge two revisions together. Creates a new revision file.

- ``flask db heads [--verbose] [--resolve-dependencies]``
    Show current available heads in the revision script directory.

- ``flask db branches [--verbose]``
    Show current branch points.

Notes:
 
- All commands also take a ``--directory DIRECTORY`` option that points to the directory containing the migration scripts. If this argument is omitted the directory used is ``migrations``.
- The default directory can also be specified as a ``directory`` argument to the ``Migrate`` constructor.
- The ``--sql`` option present in several commands performs an 'offline' mode migration. Instead of executing the database commands the SQL statements that need to be executed are printed to the console.
- Detailed documentation on these commands can be found in the `Alembic's command reference page <http://alembic.zzzcomputing.com/en/latest/api/commands.html>`_.

API Reference
-------------

The commands exposed by Flask-Migrate's command-line interface can also be accessed programmatically by importing the functions from module ``flask_migrate``. The available functions are:

- ``init(directory='migrations', multidb=False)``
    Initializes migration support for the application.

- ``revision(directory='migrations', message=None, autogenerate=False, sql=False, head='head', splice=False, branch_label=None, version_path=None, rev_id=None)``
    Creates an empty revision script.

- ``migrate(directory='migrations', message=None, sql=False, head='head', splice=False, branch_label=None, version_path=None, rev_id=None)``
    Creates an automatic revision script.

- ``edit(directory='migrations', revision='head')``
    Edit revision script(s) using $EDITOR.

- ``merge(directory='migrations', revisions='', message=None, branch_label=None, rev_id=None)``
    Merge two revisions together.  Creates a new migration file.

- ``upgrade(directory='migrations', revision='head', sql=False, tag=None)``
    Upgrades the database.

- ``downgrade(directory='migrations', revision='-1', sql=False, tag=None)``
    Downgrades the database.

- ``show(directory='migrations', revision='head')``
    Show the revision denoted by the given symbol.

- ``history(directory='migrations', rev_range=None, verbose=False)``
    Shows the list of migrations. If a range isn't given then the entire history is shown.

- ``heads(directory='migrations', verbose=False, resolve_dependencies=False)``
    Show current available heads in the script directory.

- ``branches(directory='migrations', verbose=False)``
    Show current branch points

- ``current(directory='migrations', verbose=False, head_only=False)``
    Shows the current revision of the database.
    
- ``stamp(directory='migrations', revision='head', sql=False, tag=None)``
    Sets the revision in the database to the one given as an argument, without performing any migrations.

Note: For greater scripting flexibility you can also use the API exposed by Alembic directly.
