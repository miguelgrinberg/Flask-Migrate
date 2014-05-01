import os

import click
from flask import current_app
from alembic.config import Config as AlembicConfig
from alembic import command


class _MigrateConfig(object):
    def __init__(self, db, directory):
        self.db = db
        self.directory = directory

    @property
    def metadata(self):
        """Backwards compatibility, in old releases app.extensions['migrate']
        was set to db, and env.py accessed app.extensions['migrate'].metadata
        """
        return self.db.metadata


class Migrate(object):
    def __init__(self, app=None, db=None, directory='migrations'):
        if app is not None and db is not None:
            self.init_app(app, db, directory)

    def init_app(self, app, db, directory='migrations'):
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


cli = click.Group(help='''\
Perform database migrations
''')


@cli.command()
@click.option('--directory', '-d',
              help="Migration script directory (default is 'migrations')")
def init(directory):
    "Generates a new migration"
    if directory is None:
        directory = current_app.extensions['migrate'].directory
    config = Config()
    config.set_main_option('script_location', directory)
    config.config_file_name = os.path.join(directory, 'alembic.ini')
    command.init(config, directory, 'flask')


@cli.command()
@click.option('--directory', '-d',
              help="Migration script directory (default is 'migrations')")
def current(directory):
    "Display the current revision for each database."
    config = _get_config(directory)
    command.current(config)


@cli.command()
@click.option('--rev-range', '-r',
              help="Specify a revision range; format is [start]:[end]")
@click.option('--directory', '-d',
              help="Migration script directory (default is 'migrations')")
def history(directory, rev_range):
    "List changeset scripts in chronological order."
    config = _get_config(directory)
    command.history(config, rev_range)


@cli.command()
@click.option('--sql', default=False,
              help="Don't emit SQL to database - dump to standard output "
              "instead")
@click.option('--autogenerate', default=False,
              help="Populate revision script with candidate migration "
              "operations, based on comparison of database to model")
@click.option('--message', '-m')
@click.option('--directory', '-d',
              help="Migration script directory (default is 'migrations')")
def revision(directory, message, autogenerate, sql):
    "Create a new revision file."
    config = _get_config(directory)
    command.revision(config, message, autogenerate=autogenerate, sql=sql)


@cli.command()
@click.option('--sql', default=False,
              help="Don't emit SQL to database - dump to standard output "
              "instead")
@click.option('--message', '-m')
@click.option('--directory', '-d',
              help="Migration script directory (default is 'migrations')")
def migrate(directory, message, sql):
    "Alias for 'revision --autogenerate'"
    config = _get_config(directory)
    command.revision(config, message, autogenerate=True, sql=sql)


@cli.command(short_help="Sets the revision in the database without migrating.")
@click.option('--tag',
              help="Arbitrary 'tag' name - can be used by custom env.py "
              "scripts")
@click.option('--sql', default=False,
              help="Don't emit SQL to database - dump to standard output "
              "instead")
@click.argument('revision', default='head')
@click.option('--directory', '-d',
              help="Migration script directory (default is 'migrations')")
def stamp(directory, revision, sql, tag):
    """'stamp' the revision table with the given revision; don't run any
    migrations"""
    config = _get_config(directory)
    command.stamp(config, revision, sql=sql, tag=tag)


@cli.command()
@click.option('--tag',
              help="Arbitrary 'tag' name - can be used by custom env.py "
              "scripts")
@click.option('--sql', default=False,
              help="Don't emit SQL to database - dump to standard output "
              "instead")
@click.argument('revision', default='head')
@click.option('--directory', '-d',
              help="Migration script directory (default is 'migrations')")
def upgrade(directory, revision, sql, tag):
    "Upgrade to a later version"
    config = _get_config(directory)
    command.upgrade(config, revision, sql=sql, tag=tag)


@cli.command()
@click.option('--tag',
              help="Arbitrary 'tag' name - can be used by custom env.py "
              "scripts")
@click.option('--sql', default=False,
              help="Don't emit SQL to database - dump to standard output "
              "instead")
@click.argument('revision', default='-1')
@click.option('--directory', '-d',
              help="Migration script directory (default is 'migrations')")
def downgrade(directory, revision, sql, tag):
    "Revert to a previous version"
    config = _get_config(directory)
    command.downgrade(config, revision, sql=sql, tag=tag)


@cli.command(short_help="Lists the revisions that are the source of branches")
@click.option('--directory', '-d',
              help="Migration script directory (default is 'migrations')")
def branches(directory):
    """Lists revisions that have broken the source tree into two versions
    representing two independent sets of changes"""
    config = _get_config(directory)
    command.branches(config)
