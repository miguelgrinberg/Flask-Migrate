import os
from flask import current_app
from flask.ext.script import Manager
from alembic.config import Config as AlembicConfig
from alembic import command


class _MigrateState(object):
    """Store the extension's config for each app."""

    def __init__(self, ext, app, db):
        self.ext = ext
        self.app = app
        self.db = db


class Migrate(object):
    def __init__(self, app = None, db = None, directory='migrations'):
        if app is not None and db is not None:
            self.init_app(app, db)

        self.directory = directory

    def init_app(self, app, db):
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['migrate'] = _MigrateState(self, app, db)


def _get_state(app=None):
    """Get the extensions state for a given app.

    If no app is provided, the ``current_app`` is used.

    :param app: app to get state from
    :type app: flask.Flask

    :return: extensions state for app
    :rtype: _MigrateState
    """

    app = app or current_app
    return app.extensions['migrate']


class Config(AlembicConfig):
    def get_template_directory(self):
        package_dir = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(package_dir, 'templates')


def _get_config(directory=None):
    """Build an Alembic config from a given migration directory.

    If a directory is not provided, the directory passed to the extension
    will be used as a default.

    :param directory: alternate path to Alembic config and migration scripts
    :type directory: str

    :return: Alembic config using correct path
    :rtype: alembic.config.Config
    """

    if directory is None:
        directory = _get_state().ext.directory

    config = Config(os.path.join(directory, 'alembic.ini'))
    config.set_main_option('script_location', directory)

    return config


MigrateCommand = Manager(usage = 'Perform database migrations')

@MigrateCommand.option('-d', '--directory', dest = 'directory', default = None, help = "migration script directory (default is 'migrations')")
def init(directory = None):
    "Generates a new migration"

    if directory is None:
        directory = _get_state().ext.directory

    config = Config()
    config.set_main_option('script_location', directory)
    config.config_file_name = os.path.join(directory, 'alembic.ini')
    command.init(config, directory, 'flask')

@MigrateCommand.option('-d', '--directory', dest = 'directory', default = None, help = "Migration script directory (default is 'migrations')")
def current(directory = None):
    "Display the current revision for each database."
    config = _get_config(directory)
    command.current(config)

@MigrateCommand.option('-r', '--rev-range', dest = 'rev_range', default = None, help = "Specify a revision range; format is [start]:[end]")
@MigrateCommand.option('-d', '--directory', dest = 'directory', default = None, help = "Migration script directory (default is 'migrations')")
def history(directory = None, rev_range = None):
    "List changeset scripts in chronological order."
    config = _get_config(directory)
    command.history(config)

@MigrateCommand.option('--sql', dest = 'sql', action = 'store_true', default = False, help = "Don't emit SQL to database - dump to standard output instead")
@MigrateCommand.option('--autogenerate', dest = 'autogenerate', action = 'store_true', default = False, help = "Populate revision script with andidate migration operatons, based on comparison of database to model")
@MigrateCommand.option('-m', '--message', dest = 'message', default = None)
@MigrateCommand.option('-d', '--directory', dest = 'directory', default = None, help = "Migration script directory (default is 'migrations')")
def revision(directory = None, message = None, autogenerate = False, sql = False):
    "Create a new revision file."
    config = _get_config(directory)
    command.revision(config, message, autogenerate = autogenerate, sql = sql)

@MigrateCommand.option('--sql', dest = 'sql', action = 'store_true', default = False, help = "Don't emit SQL to database - dump to standard output instead")
@MigrateCommand.option('-m', '--message', dest = 'message', default = None)
@MigrateCommand.option('-d', '--directory', dest = 'directory', default = None, help = "Migration script directory (default is 'migrations')")
def migrate(directory = None, message = None, sql = False):
    "Alias for 'revision --autogenerate'"
    config = _get_config(directory)
    command.revision(config, message, autogenerate = True, sql = sql)

@MigrateCommand.option('--tag', dest = 'tag', default = None, help = "Arbitrary 'tag' name - can be used by custom env.py scripts")
@MigrateCommand.option('--sql', dest = 'sql', action = 'store_true', default = False, help = "Don't emit SQL to database - dump to standard output instead")
@MigrateCommand.option('revision', default = None, help = "revision identifier")
@MigrateCommand.option('-d', '--directory', dest = 'directory', default = None, help = "Migration script directory (default is 'migrations')")
def stamp(directory = None, revision = 'head', sql = False, tag = None):
    "'stamp' the revision table with the given revision; don't run any migrations"
    config = _get_config(directory)
    command.stamp(config, revision, sql = sql, tag = tag)

@MigrateCommand.option('--tag', dest = 'tag', default = None, help = "Arbitrary 'tag' name - can be used by custom env.py scripts")
@MigrateCommand.option('--sql', dest = 'sql', action = 'store_true', default = False, help = "Don't emit SQL to database - dump to standard output instead")
@MigrateCommand.option('revision', nargs = '?', default = 'head', help = "revision identifier")
@MigrateCommand.option('-d', '--directory', dest = 'directory', default = None, help = "Migration script directory (default is 'migrations')")
def upgrade(directory = None, revision = 'head', sql = False, tag = None):
    "Upgrade to a later version"
    config = _get_config(directory)
    command.upgrade(config, revision, sql = sql, tag = tag)

@MigrateCommand.option('--tag', dest = 'tag', default = None, help = "Arbitrary 'tag' name - can be used by custom env.py scripts")
@MigrateCommand.option('--sql', dest = 'sql', action = 'store_true', default = False, help = "Don't emit SQL to database - dump to standard output instead")
@MigrateCommand.option('revision', nargs = '?', default = "-1", help = "revision identifier")
@MigrateCommand.option('-d', '--directory', dest = 'directory', default = None, help = "Migration script directory (default is 'migrations')")
def downgrade(directory = None, revision = '-1', sql = False, tag = None):
    "Revert to a previous version"
    config = _get_config(directory)
    command.downgrade(config, revision, sql = sql, tag = tag)
