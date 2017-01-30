import os
import shutil
import unittest
import subprocess
import shlex
import sqlite3


def run_cmd(app, cmd):
    """Run a command and return a tuple with (stdout, stderr, exit_code)"""
    os.environ['FLASK_APP'] = app
    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    (stdout, stderr) = process.communicate()
    return stdout, stderr, process.wait()


class TestMigrate(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.split(os.path.abspath(__file__))[0])
        try:
            os.remove('app1.db')
            os.remove('app2.db')
        except OSError:
            pass
        try:
            shutil.rmtree('migrations')
        except OSError:
            pass

    def tearDown(self):
        try:
            os.remove('app1.db')
            os.remove('app2.db')
        except OSError:
            pass
        try:
            shutil.rmtree('migrations')
        except OSError:
            pass

    def test_multidb_migrate_upgrade(self):
        (o, e, s) = run_cmd('app_multidb.py', 'flask db init --multidb')
        self.assertTrue(s == 0)
        (o, e, s) = run_cmd('app_multidb.py', 'flask db migrate')
        self.assertTrue(s == 0)
        (o, e, s) = run_cmd('app_multidb.py', 'flask db upgrade')
        self.assertTrue(s == 0)

        # ensure the tables are in the correct databases
        conn1 = sqlite3.connect('app1.db')
        c = conn1.cursor()
        c.execute('select name from sqlite_master')
        tables = c.fetchall()
        conn1.close()
        self.assertIn(('alembic_version',), tables)
        self.assertIn(('user',), tables)

        conn2 = sqlite3.connect('app2.db')
        c = conn2.cursor()
        c.execute('select name from sqlite_master')
        tables = c.fetchall()
        conn2.close()
        self.assertIn(('alembic_version',), tables)
        self.assertIn(('group',), tables)

        # ensure the databases can be written to
        from .app_multidb import db, User, Group
        db.session.add(User(name='test'))
        db.session.add(Group(name='group'))
        db.session.commit()

        # ensure the downgrade works
        (o, e, s) = run_cmd('app_multidb.py', 'flask db downgrade')
        self.assertTrue(s == 0)

        conn1 = sqlite3.connect('app1.db')
        c = conn1.cursor()
        c.execute('select name from sqlite_master')
        tables = c.fetchall()
        conn1.close()
        self.assertIn(('alembic_version',), tables)
        self.assertNotIn(('user',), tables)

        conn2 = sqlite3.connect('app2.db')
        c = conn2.cursor()
        c.execute('select name from sqlite_master')
        tables = c.fetchall()
        conn2.close()
        self.assertIn(('alembic_version',), tables)
        self.assertNotIn(('group',), tables)
