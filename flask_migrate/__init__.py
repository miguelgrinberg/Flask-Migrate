import os
import argparse
from flask.ext.script import Command
from flask.ext.script import Manager
from flask.ext.script import Option
from alembic import __version__ as __alembic_version__
from alembic.config import Config as AlembicConfig
from alembic import command


alembic_version = tuple([int(v) for v in __alembic_version__.split('.')[0:3]])


class Config(AlembicConfig):
    def get_template_directory(self):
        package_dir = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(package_dir, 'templates')


class Migrate(object):
    config_cls = Config

    def __init__(self, app=None, db=None, directory='migrations', **kwargs):
        self.directory = directory
        self.db = db
        self.directory = directory
        self.configure_args = kwargs
        if app is not None and db is not None:
            self.init_app(app, db, directory, **kwargs)

    def init_app(self, app, db, directory=None, **kwargs):
        self.directory = directory or self.directory
        self.db = db
        self.configure_args = kwargs or self.configure_args
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['migrate'] = self

    @property
    def metadata(self):
        """
        Backwards compatibility, in old releases app.extensions['migrate']
        was set to db, and env.py accessed app.extensions['migrate'].metadata
        """
        return self.db.metadata

    @classmethod
    def map_commands(cls):
        return dict(
            init=InitCommand,
            revision=RevisionCommand,
            migrate=AMigrateCommand,
            edit=EditCommand,
            merge=MergeCommand,
            upgrade=UpgradeCommand,
            downgrade=DowngradeCommand,
            show=ShowCommand,
            history=HistoryCommand,
            heads=HeadsCommand,
            branches=BranchesCommand,
            current=CurrentCommand,
            stamp=StampCommand,
        )

    def make_command(self):
        ret = Manager(usage='Perform database migrations')
        for cmd, cls in self.map_commands().items():
            ret.add_command(cmd, cls(self))
        return ret

    def get_config(self, directory, x_arg=None, opts=None):
        if directory is None:
            directory = self.directory
        config = self.config_cls(os.path.join(directory, 'alembic.ini'))
        config.set_main_option('script_location', directory)
        if config.cmd_opts is None:
            config.cmd_opts = argparse.Namespace()
        for opt in opts or []:
            setattr(config.cmd_opts, opt, True)
        if x_arg is not None:
            if not getattr(config.cmd_opts, 'x', None):
                setattr(config.cmd_opts, 'x', [x_arg])
            else:
                config.cmd_opts.x.append(x_arg)
        return config


# noinspection PyAbstractClass
class BaseCommand(Command):
    def __init__(self, fmobj):
        super(Command, self).__init__()
        self.fmobj = fmobj


class InitCommand(BaseCommand):
    """Generates a new migration"""

    option_list = (
        Option('-d', '--directory', dest='directory', default=None,
               help="migration script directory (default is 'migrations')"),
        Option('--multidb', dest='multidb', action='store_true', default=False,
               help="Multiple databases migraton (default is False)"),
    )

    def run(self, directory=None, multidb=False):
        if directory is None:
            directory = self.fmobj.directory
        config = self.fmobj.config_cls()
        config.set_main_option('script_location', directory)
        config.config_file_name = os.path.join(directory, 'alembic.ini')
        if multidb:
            command.init(config, directory, 'flask-multidb')
        else:
            command.init(config, directory, 'flask')


class RevisionCommand(BaseCommand):
    """Create a new revision file."""
    option_list = (
        Option('--rev-id', dest='rev_id', default=None, help=(
            'Specify a hardcoded revision id instead of generating one')),
        Option('--version-path', dest='version_path', default=None,
               help='Specify specific path from config for version file'),
        Option('--branch-label', dest='branch_label', default=None, help=(
            'Specify a branch label to apply to the new revision')),
        Option('--splice', dest='splice', action='store_true', default=False,
               help='Allow a non-head revision as the "head" to splice onto'),
        Option('--head', dest='head', default='head',
               help=('Specify head revision or <branchname>@head to '
                     'base new revision on')),
        Option('--sql', dest='sql', action='store_true', default=False, help=(
            "Don't emit SQL to database - dump to standard output instead")),
        Option('--autogenerate', dest='autogenerate', action='store_true',
               default=False, help=(
                'Populate revision script with candidate migration operations,'
                ' based on comparison of database to model')),
        Option('-m', '--message', dest='message', default=None),
        Option('-d', '--directory', dest='directory', default=None, help=(
            "migration script directory (default is 'migrations')")),
    )

    def run(self, directory=None, message=None, autogenerate=False, sql=False,
            head='head', splice=False, branch_label=None, version_path=None,
            rev_id=None):
        config = self.fmobj.get_config(directory)
        if alembic_version >= (0, 7, 0):
            command.revision(config, message, autogenerate=autogenerate,
                             sql=sql, head=head, splice=splice,
                             branch_label=branch_label,
                             version_path=version_path, rev_id=rev_id)
        else:
            command.revision(config, message, autogenerate=autogenerate,
                             sql=sql)


class AMigrateCommand(BaseCommand):
    """Alias for 'revision --autogenerate'"""

    option_list = (
        Option('--rev-id', dest='rev_id', default=None, help=(
            'Specify a hardcoded revision id instead of generating one')),
        Option('--version-path', dest='version_path', default=None,
               help='Specify specific path from config for version file'),
        Option('--branch-label', dest='branch_label', default=None,
               help='Specify a branch label to apply to the new revision'),
        Option('--splice', dest='splice', action='store_true', default=False,
               help='Allow a non-head revision as the "head" to splice onto'),
        Option('--head', dest='head', default='head',
               help=('Specify head revision or <branchname>@head to '
                     'base new revision on')),
        Option('--sql', dest='sql', action='store_true', default=False, help=(
            "Don't emit SQL to database - dump to standard output instead")),
        Option('-m', '--message', dest='message', default=None),
        Option('-d', '--directory', dest='directory', default=None, help=(
            "migration script directory (default is 'migrations')")),
    )

    def run(self, directory=None, message=None, sql=False, head='head',
            splice=False, branch_label=None, version_path=None, rev_id=None):
        config = self.fmobj.get_config(directory, opts=['autogenerate'])
        if alembic_version >= (0, 7, 0):
            command.revision(config, message, autogenerate=True, sql=sql,
                             head=head,
                             splice=splice, branch_label=branch_label,
                             version_path=version_path, rev_id=rev_id)
        else:
            command.revision(config, message, autogenerate=True, sql=sql)


class EditCommand(BaseCommand):
    """Edit current revision."""

    option_list = (
        Option('revision', nargs='?', default='head',
               help="revision identifier"),
        Option('-d', '--directory', dest='directory', default=None,
               help="migration script directory (default is 'migrations')"),
    )

    def run(self, revision='current', directory=None):
        if alembic_version >= (0, 8, 0):
            config = self.fmobj.get_config(directory)
            command.edit(config, revision)
        else:
            raise RuntimeError('Alembic 0.8.0 or greater is required')


class MergeCommand(BaseCommand):
    """Merge two revisions together.  Creates a new migration file"""

    option_list = (
        Option('--rev-id', dest='rev_id', default=None, help=(
            'Specify a hardcoded revision id instead of generating one')),
        Option('--branch-label', dest='branch_label', default=None,
               help='Specify a branch label to apply to the new revision'),
        Option('-m', '--message', dest='message', default=None),
        Option('revisions', nargs='+',
               help='one or more revisions, or "heads" for all heads'),
        Option('-d', '--directory', dest='directory', default=None,
               help="migration script directory (default is 'migrations')"),
    )

    def run(self, directory=None, revisions='', message=None,
            branch_label=None, rev_id=None):
        if alembic_version >= (0, 7, 0):
            config = self.fmobj.get_config(directory)
            command.merge(config, revisions, message=message,
                          branch_label=branch_label, rev_id=rev_id)
        else:
            raise RuntimeError('Alembic 0.7.0 or greater is required')


class UpgradeCommand(BaseCommand):
    """Upgrade to a later version"""

    option_list = (
        Option('--tag', dest='tag', default=None, help=(
            "Arbitrary 'tag' name - can be used by custom env.py scripts")),
        Option('--sql', dest='sql', action='store_true', default=False, help=(
            "Don't emit SQL to database - dump to standard output instead")),
        Option('revision', nargs='?', default='head',
               help="revision identifier"),
        Option('-d', '--directory', dest='directory', default=None,
               help="migration script directory (default is 'migrations')"),
        Option('-x', '--x-arg', dest='x_arg', default=None,
               help="Additional arguments consumed by custom env.py scripts"),
    )

    def run(self, directory=None, revision='head', sql=False, tag=None,
            x_arg=None):
        config = self.fmobj.get_config(directory, x_arg=x_arg)
        command.upgrade(config, revision, sql=sql, tag=tag)


class DowngradeCommand(BaseCommand):
    """Revert to a previous version"""

    option_list = (
        Option('--tag', dest='tag', default=None, help=(
            "Arbitrary 'tag' name - can be used by custom env.py scripts")),
        Option('--sql', dest='sql', action='store_true', default=False, help=(
            "Don't emit SQL to database - dump to standard output instead")),
        Option('revision', nargs='?', default="-1",
               help="revision identifier"),
        Option('-d', '--directory', dest='directory', default=None,
               help="migration script directory (default is 'migrations')"),
        Option('-x', '--x-arg', dest='x_arg', default=None,
               help="Additional arguments consumed by custom env.py scripts"),
    )

    def run(self, directory=None, revision='-1', sql=False, tag=None,
            x_arg=None):
        config = self.fmobj.get_config(directory, x_arg=x_arg)
        if sql and revision == '-1':
            revision = 'head:-1'
        command.downgrade(config, revision, sql=sql, tag=tag)


class ShowCommand(BaseCommand):
    """Show the revision denoted by the given symbol."""

    option_list = (
        Option('revision', nargs='?', default="head",
               help="revision identifier"),
        Option('-d', '--directory', dest='directory', default=None,
               help="migration script directory (default is 'migrations')"),
    )

    def run(self, directory=None, revision='head'):
        if alembic_version >= (0, 7, 0):
            config = self.fmobj.get_config(directory)
            command.show(config, revision)
        else:
            raise RuntimeError('Alembic 0.7.0 or greater is required')


class HistoryCommand(BaseCommand):
    """List changeset scripts in chronological order."""

    option_list = (
        Option('-v', '--verbose', dest='verbose', action='store_true',
               default=False, help='Use more verbose output'),
        Option('-r', '--rev-range', dest='rev_range', default=None,
               help='Specify a revision range; format is [start]:[end]'),
        Option('-d', '--directory', dest='directory', default=None,
               help="migration script directory (default is 'migrations')"),
    )

    def run(self, directory=None, rev_range=None, verbose=False):
        config = self.fmobj.get_config(directory)
        if alembic_version >= (0, 7, 0):
            command.history(config, rev_range, verbose=verbose)
        else:
            command.history(config, rev_range)


class HeadsCommand(BaseCommand):
    """Show current available heads in the script directory"""

    option_list = (
        Option('--resolve-dependencies', dest='resolve_dependencies',
               action='store_true', default=False,
               help='Treat dependency versions as down revisions'),
        Option('-v', '--verbose', dest='verbose', action='store_true',
               default=False, help='Use more verbose output'),
        Option('-d', '--directory', dest='directory', default=None,
               help="migration script directory (default is 'migrations')"),
    )

    def run(self, directory=None, verbose=False, resolve_dependencies=False):
        if alembic_version >= (0, 7, 0):
            config = self.fmobj.get_config(directory)
            command.heads(config, verbose=verbose,
                          resolve_dependencies=resolve_dependencies)
        else:
            raise RuntimeError('Alembic 0.7.0 or greater is required')


class BranchesCommand(BaseCommand):
    """Show current branch points"""

    option_list = (
        Option('-v', '--verbose', dest='verbose', action='store_true',
               default=False, help='Use more verbose output'),
        Option('-d', '--directory', dest='directory', default=None,
               help="migration script directory (default is 'migrations')"),
    )

    def run(self, directory=None, verbose=False):
        config = self.fmobj.get_config(directory)
        if alembic_version >= (0, 7, 0):
            command.branches(config, verbose=verbose)
        else:
            command.branches(config)


class CurrentCommand(BaseCommand):
    """Display the current revision for each database."""

    option_list = (
        Option('--head-only', dest='head_only', action='store_true',
               default=False,
               help='Deprecated. Use --verbose for additional output'),
        Option('-v', '--verbose', dest='verbose', action='store_true',
               default=False, help='Use more verbose output'),
        Option('-d', '--directory', dest='directory', default=None,
               help="migration script directory (default is 'migrations')"),
    )

    def run(self, directory=None, verbose=False, head_only=False):
        config = self.fmobj.get_config(directory)
        if alembic_version >= (0, 7, 0):
            command.current(config, verbose=verbose, head_only=head_only)
        else:
            command.current(config)


class StampCommand(BaseCommand):
    """'stamp' the revision table with the given revision; don't run any
    migrations"""

    option_list = (
        Option('--tag', dest='tag', default=None, help=(
            "Arbitrary 'tag' name - can be used by custom env.py scripts")),
        Option('--sql', dest='sql', action='store_true', default=False,
               help=("Don't emit SQL to database - dump to standard "
                     "output instead")),
        Option('revision', default=None, help="revision identifier"),
        Option('-d', '--directory', dest='directory', default=None,
               help="migration script directory (default is 'migrations')"),
    )

    def run(self, directory=None, revision='head', sql=False, tag=None):
        config = self.fmobj.get_config(directory)
        command.stamp(config, revision, sql=sql, tag=tag)
