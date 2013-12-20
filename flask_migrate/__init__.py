import os
from flask import current_app
from flask.ext.script import Manager
from alembic.config import Config as AlembicConfig
from alembic import command

class _MigrateConfig(object):
    def __init__(self, db, directory):
        self.db = db
        self.directory = directory

    @property
    def metadata(self):
        """Backwards compatibility, in old releases app.extensions['migrate']
        was set to db, and env.py accessed app.extensions['migrate'].metadata"""
        return self.db.metadata

class Migrate(object):
    def __init__(self, app = None, db = None, directory = 'migrations'):
        if app is not None and db is not None:
            self.init_app(app, db, directory)

    def init_app(self, app, db, directory = 'migrations'):
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['migrate'] = _MigrateConfig(db, directory)

class Config(AlembicConfig):
    def get_template_directory(self):
        package_dir = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(package_dir, 'templates')

def _get_config(directory):
    if directory is None:
        directory = current_app.extensions['migrate'].directory
    config = Config(os.path.join(directory, 'alembic.ini'))
    config.set_main_option('script_location', directory)
    return config

MigrateCommand = Manager(usage = 'Perform database migrations')

@MigrateCommand.option('-d', '--directory', dest = 'directory', default = None, help = "migration script directory (default is 'migrations')")
def init(directory = None):
    "Generates a new migration"
    if directory is None:
        directory = current_app.extensions['migrate'].directory
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
    command.history(config, rev_range)

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
