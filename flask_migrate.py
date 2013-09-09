import os
from flask.ext.script import Manager
from alembic.config import Config as AlembicConfig
from alembic import command

class Migrate(object):
    def __init__(self, app = None, db = None):
        self.init_app(app, db)
        
    def init_app(self, app, db):
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['migrate'] = db
        
class Config(AlembicConfig):
    def get_template_directory(self):
        package_dir = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(package_dir, 'templates')

def _get_config(directory):
    config = Config(os.path.join(directory, 'alembic.ini'))
    config.set_main_option('script_location', directory)
    return config

MigrateCommand = Manager(usage = 'Perform database migrations')
    
@MigrateCommand.option('-d', '--directory', dest = 'directory', default = 'migrations', help = "migration script directory (default is 'migrations')")
def init(directory):
    "Generates a new migration"
    config = Config()
    config.set_main_option('script_location', directory)
    config.config_file_name = 'alembic.ini'
    command.init(config, directory, 'flask')
    os.rename('alembic.ini', os.path.join(directory, 'alembic.ini'))

@MigrateCommand.option('-d', '--directory', dest = 'directory', default = 'migrations', help = "Migration script directory (default is 'migrations')")
def current(directory):
    "Display the current revision for each database."
    config = _get_config(directory)
    command.current(config)

@MigrateCommand.option('-r', '--rev-range', dest = 'rev_range', default = None, help = "Specify a revision range; format is [start]:[end]")
@MigrateCommand.option('-d', '--directory', dest = 'directory', default = 'migrations', help = "Migration script directory (default is 'migrations')")
def history(directory, rev_range):
    "List changeset scripts in chronological order."
    config = _get_config(directory)
    command.history(config)

@MigrateCommand.option('--sql', dest = 'sql', action = 'store_true', default = False, help = "Don't emit SQL to database - dump to standard output instead")
@MigrateCommand.option('--autogenerate', dest = 'autogenerate', action = 'store_true', default = False, help = "Populate revision script with andidate migration operatons, based on comparison of database to model")
@MigrateCommand.option('-m', '--message', dest = 'message', default = None)
@MigrateCommand.option('-d', '--directory', dest = 'directory', default = 'migrations', help = "Migration script directory (default is 'migrations')")
def revision(directory, message, autogenerate, sql):
    "Create a new revision file."
    config = _get_config(directory)
    command.revision(config, message, autogenerate = autogenerate, sql = sql)

@MigrateCommand.option('--sql', dest = 'sql', action = 'store_true', default = False, help = "Don't emit SQL to database - dump to standard output instead")
@MigrateCommand.option('-m', '--message', dest = 'message', default = None)
@MigrateCommand.option('-d', '--directory', dest = 'directory', default = 'migrations', help = "Migration script directory (default is 'migrations')")
def migrate(directory, message, sql):
    "Alias for 'revision --autogenerate'"
    config = _get_config(directory)
    command.revision(config, message, autogenerate = True, sql = sql)

@MigrateCommand.option('--tag', dest = 'tag', default = None, help = "Arbitrary 'tag' name - can be used by custom env.py scripts")
@MigrateCommand.option('--sql', dest = 'sql', action = 'store_true', default = False, help = "Don't emit SQL to database - dump to standard output instead")
@MigrateCommand.option('revision', default = None, help = "revision identifier")
@MigrateCommand.option('-d', '--directory', dest = 'directory', default = 'migrations', help = "Migration script directory (default is 'migrations')")
def stamp(directory, revision, sql, tag):
    "'stamp' the revision table with the given revision; don't run any migrations"
    config = _get_config(directory)
    command.stamp(config, revision, sql = sql, tag = tag)

@MigrateCommand.option('--tag', dest = 'tag', default = None, help = "Arbitrary 'tag' name - can be used by custom env.py scripts")
@MigrateCommand.option('--sql', dest = 'sql', action = 'store_true', default = False, help = "Don't emit SQL to database - dump to standard output instead")
@MigrateCommand.option('revision', nargs = '?', default = 'head', help = "revision identifier")
@MigrateCommand.option('-d', '--directory', dest = 'directory', default = 'migrations', help = "Migration script directory (default is 'migrations')")
def upgrade(directory, revision, sql, tag):
    "Upgrade to a later version"
    config = _get_config(directory)
    command.upgrade(config, revision, sql = sql, tag = tag)
    
@MigrateCommand.option('--tag', dest = 'tag', default = None, help = "Arbitrary 'tag' name - can be used by custom env.py scripts")
@MigrateCommand.option('--sql', dest = 'sql', action = 'store_true', default = False, help = "Don't emit SQL to database - dump to standard output instead")
@MigrateCommand.option('revision', nargs = '?', default = "-1", help = "revision identifier")
@MigrateCommand.option('-d', '--directory', dest = 'directory', default = 'migrations', help = "Migration script directory (default is 'migrations')")
def downgrade(directory, revision, sql, tag):
    "Revert to a previous version"
    config = _get_config(directory)
    command.downgrade(config, revision, sql = sql, tag = tag)
    