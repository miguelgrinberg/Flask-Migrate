# Flask-Migrate Change Log

## Release 2.1.1 - 2017-08-28

- Make the `directory` argument to `get_config()` optional (#168)

## Release 2.1.0 - 2017-07-27

- Removed dependency on Flask-Script from setup.py (#165)

## Release 2.0.4 - 2017-05-30

- Support -x arguments in "migrate" command (#148)

## Release 2.0.3 - 2017-01-29

- Support multiple -x arguments in the Flask-Script interface (#103)

## Release 2.0.2 - 2016-12-09

- Support passing alembic context kwargs from constructor into init_app (#138)

## Release 2.0.1 - 2016-11-13

- Fix flake8 warnings in Alembic templates (#136)

## Release 2.0.0 - 2016-07-31

- Added Travis CI builds for Python 3.5
- Support for the new Flask CLI based on Click

## Release 1.8.1 - 2016-07-10

- Allow to init_app to work correctly when db is given in constructor (#118)

## Release 1.8.0 - 2016-02-23

- Allow db to be given in constructor, while app is given later in `init_app`
- Added missing Python 2 classifiers in setup script
- Various documentation updates

## Release 1.7.0 - 2015-12-27

- Added `migrate.configure` decorator to register configuration callbacks
- Documentation updates

## Release 1.6.0 - 2015-09-17

- Added support for Alembic's `edit` command
- Allow migration directory to be given in constructor and not in `init_app`

## Release 1.5.1 - 2015-08-23

- Do not generate a migration if no schema changes are found
- Merge command now supports multiple arguments

## Release 1.5.0 - 2015-08-01

- Support for multiple databases
- Added support for Alembic's `-x` option
- Added sane default for `db downgrade --sql` command

## Release 1.4.0 - 2015-04-26

- Any `kwargs` given to the `Migrate` constructor or `init_app` method are passed to Alembic as additional configuration

## Release 1.3.1 - 2015-03-19

- Handle Alembic versions that have non-integer parts.

## Release 1.3.0 - 2014-11-30

- Support for new commands and options introduced with Alembic 0.7
- Pep8 improvements
- Documentation improvements
- Added Travis CI builds
- Added Python 3 classifier to setup script
- Fixed unit tests to run on Python 3

## Release 1.2.0 - 2014-01-19

- Support Alembic's `branch` command

## Release 1.1.1 - 2014-01-06

- Included tests in release package

## Release 1.1.0 - 2013-12-19

- Support a custom migrations directory
- Pass revision range to Alembic's `history` command

## Release 1.0.0 - 2013-12-03

- First official release
