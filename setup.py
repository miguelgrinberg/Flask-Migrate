"""
Flask-Migrate
--------------

SQLAlchemy database migrations for Flask applications using Alembic.
"""
from setuptools import setup


VERSION = open('__version__').read()

setup(
    name='Flask-Migrate',
    version=VERSION,
    url='http://github.com/miguelgrinberg/flask-migrate/',
    license='MIT',
    author='Miguel Grinberg',
    author_email='miguelgrinberg50@gmail.com',
    description=('SQLAlchemy database migrations for Flask applications '
                 'using Alembic'),
    long_description=__doc__,
    packages=['flask_migrate'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask>=0.9',
        'Flask-SQLAlchemy>=1.0',
        'alembic>=0.7'
    ],
    entry_points={
        'flask.commands': [
            'db=flask_migrate.cli:db'
        ],
    },
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
