from __future__ import print_function

import os
import shutil
import unittest
import subprocess
import shlex


def run_cmd(cmd):
    """Run a command and return a tuple with (stdout, stderr, exit_code)"""
    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    (stdout, stderr) = process.communicate()
    return stdout, stderr, process.wait()


class TestMigrate(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.split(os.path.abspath(__file__))[0])
        try:
            os.remove('app.db')
            os.remove('app1.db')
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
            os.remove('app1.db')
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
        (o, e, s) = run_cmd('python app_multidb.py db init -m')
        self.assertTrue(s == 0)
        dir_name = os.path.dirname(os.path.realpath(__file__))
        src = os.path.join(dir_name, "alembic.ini")
        dest = os.path.join(dir_name, "migrations", "alembic.ini")
        shutil.copyfile(src, dest)
        src = os.path.join(dir_name, "env.py.copy")
        dest = os.path.join(dir_name, "migrations", "env.py")
        shutil.copyfile(src, dest)
        (o, e, s) = run_cmd('python app_multidb.py db migrate')
        self.assertTrue(s == 0)
        (o, e, s) = run_cmd('python app_multidb.py db upgrade')
        self.assertTrue(s == 0)

        from .app_multidb import db, User
        db.session.add(User(name='test'))
        db.session.commit()


if __name__ == '__main__':
    unittest.main()
