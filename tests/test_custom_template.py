import os
import shutil
import unittest
import subprocess
import shlex


def run_cmd(app, cmd):
    """Run a command and return a tuple with (stdout, stderr, exit_code)"""
    os.environ['FLASK_APP'] = app
    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    (stdout, stderr) = process.communicate()
    print('\n$ ' + cmd)
    print(stdout.decode('utf-8'))
    print(stderr.decode('utf-8'))
    return stdout, stderr, process.wait()


class TestMigrate(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.split(os.path.abspath(__file__))[0])
        try:
            os.remove('app.db')
        except OSError:
            pass
        try:
            shutil.rmtree('migrations')
        except OSError:
            pass
        try:
            shutil.rmtree('temp_folder')
        except OSError:
            pass

    def tearDown(self):
        try:
            os.remove('app.db')
        except OSError:
            pass
        try:
            shutil.rmtree('migrations')
        except OSError:
            pass
        try:
            shutil.rmtree('temp_folder')
        except OSError:
            pass

    def test_alembic_version(self):
        from flask_migrate import alembic_version
        self.assertEqual(len(alembic_version), 3)
        for v in alembic_version:
            self.assertTrue(isinstance(v, int))

    def test_migrate_upgrade(self):
        (o, e, s) = run_cmd('app.py', 'flask db init -t ./custom_template')
        self.assertTrue(s == 0)
        (o, e, s) = run_cmd('app.py', 'flask db migrate')
        self.assertTrue(s == 0)
        (o, e, s) = run_cmd('app.py', 'flask db upgrade')
        self.assertTrue(s == 0)

        from .app import app, db, User
        with app.app_context():
            db.engine.dispose()
            db.session.add(User(name='test'))
            db.session.commit()

        with open('migrations/README', 'rt') as f:
            assert f.readline().strip() == 'Custom template.'
        with open('migrations/alembic.ini', 'rt') as f:
            assert f.readline().strip() == '# Custom template'
        with open('migrations/env.py', 'rt') as f:
            assert f.readline().strip() == '# Custom template'
        with open('migrations/script.py.mako', 'rt') as f:
            assert f.readline().strip() == '# Custom template'
