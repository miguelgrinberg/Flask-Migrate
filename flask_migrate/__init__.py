import os
from flask import current_app
from flask.ext.script import Manager
from alembic import __version__ as __alembic_version__
from alembic.config import Config as AlembicConfig
from alembic import command
import re

# Ignore any possible string appendix when retrieving version, e.g. `post1` in `0.7.5.post1`
alembic_version = tuple([int(v) for v in re.search('([0-9]?\.[0-9]?\.[0-9]?)', __alembic_version__).group(1).split('.')])

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

MigrateCommand = Manager(usage='Perform database migrations')


@MigrateCommand.option('-d', '--directory', dest='directory', default=None,
                       help=("migration script directory (default is "
                             "'migrations')"))
def init(directory=None):
    """Generates a new migration"""
    if directory is None:
        directory = current_app.extensions['migrate'].directory
    config = Config()
    config.set_main_option('script_location', directory)
    config.config_file_name = os.path.join(directory, 'alembic.ini')
    command.init(config, directory, 'flask')


@MigrateCommand.option('--rev-id', dest='rev_id', default=None,
                       help=('Specify a hardcoded revision id instead of '
                             'generating one'))
@MigrateCommand.option('--version-path', dest='version_path', default=None,
                       help=('Specify specific path from config for version '
                             'file'))
@MigrateCommand.option('--branch-label', dest='branch_label', default=None,
                       help=('Specify a branch label to apply to the new '
                             'revision'))
@MigrateCommand.option('--splice', dest='splice', action='store_true',
                       default=False,
                       help=('Allow a non-head revision as the "head" to '
                             'splice onto'))
@MigrateCommand.option('--head', dest='head', default='head',
                       help=('Specify head revision or <branchname>@head to '
                             'base new revision on'))
@MigrateCommand.option('--sql', dest='sql', action='store_true', default=False,
                       help=("Don't emit SQL to database - dump to standard "
                             "output instead"))
@MigrateCommand.option('--autogenerate', dest='autogenerate',
                       action='store_true', default=False,
                       help=('Populate revision script with andidate migration '
                             'operatons, based on comparison of database to '
                             'model'))
@MigrateCommand.option('-m', '--message', dest='message', default=None)
@MigrateCommand.option('-d', '--directory', dest='directory', default=None,
                       help=("migration script directory (default is "
                             "'migrations')"))
def revision(directory=None, message=None, autogenerate=False, sql=False,
             head='head', splice=False, branch_label=None, version_path=None,
             rev_id=None):
    """Create a new revision file."""
    config = _get_config(directory)
    if alembic_version >= (0, 7, 0):
        command.revision(config, message, autogenerate=autogenerate, sql=sql,
                         head=head, splice=splice, branch_label=branch_label,
                         version_path=version_path, rev_id=rev_id)
    else:
        command.revision(config, message, autogenerate=autogenerate, sql=sql)


@MigrateCommand.option('--rev-id', dest='rev_id', default=None,
                       help=('Specify a hardcoded revision id instead of '
                             'generating one'))
@MigrateCommand.option('--version-path', dest='version_path', default=None,
                       help=('Specify specific path from config for version '
                             'file'))
@MigrateCommand.option('--branch-label', dest='branch_label', default=None,
                       help=('Specify a branch label to apply to the new '
                             'revision'))
@MigrateCommand.option('--splice', dest='splice', action='store_true',
                       default=False,
                       help=('Allow a non-head revision as the "head" to '
                             'splice onto'))
@MigrateCommand.option('--head', dest='head', default='head',
                       help=('Specify head revision or <branchname>@head to '
                             'base new revision on'))
@MigrateCommand.option('--sql', dest='sql', action='store_true', default=False,
                       help=("Don't emit SQL to database - dump to standard "
                             "output instead"))
@MigrateCommand.option('-m', '--message', dest='message', default=None)
@MigrateCommand.option('-d', '--directory', dest='directory', default=None,
                       help=("migration script directory (default is "
                             "'migrations')"))
def migrate(directory=None, message=None, sql=False, head='head', splice=False,
            branch_label=None, version_path=None, rev_id=None):
    """Alias for 'revision --autogenerate'"""
    config = _get_config(directory)
    if alembic_version >= (0, 7, 0):
        command.revision(config, message, autogenerate=True, sql=sql, head=head,
                         splice=splice, branch_label=branch_label,
                         version_path=version_path, rev_id=rev_id)
    else:
        command.revision(config, message, autogenerate=True, sql=sql)


@MigrateCommand.option('--rev-id', dest='rev_id', default=None,
                       help=('Specify a hardcoded revision id instead of '
                             'generating one'))
@MigrateCommand.option('--branch-label', dest='branch_label', default=None,
                       help=('Specify a branch label to apply to the new '
                             'revision'))
@MigrateCommand.option('-m', '--message', dest='message', default=None)
@MigrateCommand.option('revisions',
                       help='one or more revisions, or "heads" for all heads')
@MigrateCommand.option('-d', '--directory', dest='directory', default=None,
                       help=("migration script directory (default is "
                             "'migrations')"))
def merge(directory=None, revisions='', message=None, branch_label=None,
          rev_id=None):
    """Merge two revisions together.  Creates a new migration file"""
    if alembic_version >= (0, 7, 0):
        config = _get_config(directory)
        command.merge(config, revisions, message=message,
                      branch_label=branch_label, rev_id=rev_id)
    else:
        raise RuntimeError('Alembic 0.7.0 or greater is required')


@MigrateCommand.option('--tag', dest='tag', default=None,
                       help=("Arbitrary 'tag' name - can be used by custom "
                             "env.py scripts"))
@MigrateCommand.option('--sql', dest='sql', action='store_true', default=False,
                       help=("Don't emit SQL to database - dump to standard "
                             "output instead"))
@MigrateCommand.option('revision', nargs='?', default='head',
                       help="revision identifier")
@MigrateCommand.option('-d', '--directory', dest='directory', default=None,
                       help=("migration script directory (default is "
                             "'migrations')"))
def upgrade(directory=None, revision='head', sql=False, tag=None):
    """Upgrade to a later version"""
    config = _get_config(directory)
    command.upgrade(config, revision, sql=sql, tag=tag)


@MigrateCommand.option('--tag', dest='tag', default=None,
                       help=("Arbitrary 'tag' name - can be used by custom "
                             "env.py scripts"))
@MigrateCommand.option('--sql', dest='sql', action='store_true', default=False,
                       help=("Don't emit SQL to database - dump to standard "
                             "output instead"))
@MigrateCommand.option('revision', nargs='?', default="-1",
                       help="revision identifier")
@MigrateCommand.option('-d', '--directory', dest='directory', default=None,
                       help=("migration script directory (default is "
                             "'migrations')"))
def downgrade(directory=None, revision='-1', sql=False, tag=None):
    """Revert to a previous version"""
    config = _get_config(directory)
    command.downgrade(config, revision, sql=sql, tag=tag)


@MigrateCommand.option('revision', nargs='?', default="head",
                       help="revision identifier")
@MigrateCommand.option('-d', '--directory', dest='directory', default=None,
                       help=("migration script directory (default is "
                             "'migrations')"))
def show(directory=None, revision='head'):
    """Show the revision denoted by the given symbol."""
    if alembic_version >= (0, 7, 0):
        config = _get_config(directory)
        command.show(config, revision)
    else:
        raise RuntimeError('Alembic 0.7.0 or greater is required')


@MigrateCommand.option('-v', '--verbose', dest='verbose', action='store_true',
                       default=False, help='Use more verbose output')
@MigrateCommand.option('-r', '--rev-range', dest='rev_range', default=None,
                       help='Specify a revision range; format is [start]:[end]')
@MigrateCommand.option('-d', '--directory', dest='directory', default=None,
                       help=("migration script directory (default is "
                             "'migrations')"))
def history(directory=None, rev_range=None, verbose=False):
    """List changeset scripts in chronological order."""
    config = _get_config(directory)
    if alembic_version >= (0, 7, 0):
        command.history(config, rev_range, verbose=verbose)
    else:
        command.history(config, rev_range)


@MigrateCommand.option('--resolve-dependencies', dest='resolve_dependencies',
                       action='store_true', default=False,
                       help='Treat dependency versions as down revisions')
@MigrateCommand.option('-v', '--verbose', dest='verbose', action='store_true',
                       default=False, help='Use more verbose output')
@MigrateCommand.option('-d', '--directory', dest='directory', default=None,
                       help=("migration script directory (default is "
                             "'migrations')"))
def heads(directory=None, verbose=False, resolve_dependencies=False):
    """Show current available heads in the script directory"""
    if alembic_version >= (0, 7, 0):
        config = _get_config(directory)
        command.heads(config, verbose=verbose,
                      resolve_dependencies=resolve_dependencies)
    else:
        raise RuntimeError('Alembic 0.7.0 or greater is required')


@MigrateCommand.option('-v', '--verbose', dest='verbose', action='store_true',
                       default=False, help='Use more verbose output')
@MigrateCommand.option('-d', '--directory', dest='directory', default=None,
                       help=("migration script directory (default is "
                             "'migrations')"))
def branches(directory=None, verbose=False):
    """Show current branch points"""
    config = _get_config(directory)
    if alembic_version >= (0, 7, 0):
        command.branches(config, verbose=verbose)
    else:
        command.branches(config)


@MigrateCommand.option('--head-only', dest='head_only', action='store_true',
                       default=False,
                       help='Deprecated. Use --verbose for additional output')
@MigrateCommand.option('-v', '--verbose', dest='verbose', action='store_true',
                       default=False, help='Use more verbose output')
@MigrateCommand.option('-d', '--directory', dest='directory', default=None,
                       help=("migration script directory (default is "
                             "'migrations')"))
def current(directory=None, verbose=False, head_only=False):
    """Display the current revision for each database."""
    config = _get_config(directory)
    if alembic_version >= (0, 7, 0):
        command.current(config, verbose=verbose, head_only=head_only)
    else:
        command.current(config)


@MigrateCommand.option('--tag', dest='tag', default=None,
                       help=("Arbitrary 'tag' name - can be used by custom "
                             "env.py scripts"))
@MigrateCommand.option('--sql', dest='sql', action='store_true', default=False,
                       help=("Don't emit SQL to database - dump to standard "
                             "output instead"))
@MigrateCommand.option('revision', default=None, help="revision identifier")
@MigrateCommand.option('-d', '--directory', dest='directory', default=None,
                       help=("migration script directory (default is "
                             "'migrations')"))
def stamp(directory=None, revision='head', sql=False, tag=None):
    """'stamp' the revision table with the given revision; don't run any
    migrations"""
    config = _get_config(directory)
    command.stamp(config, revision, sql=sql, tag=tag)
