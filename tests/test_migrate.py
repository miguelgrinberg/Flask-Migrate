import os
import shlex
import shutil
import subprocess
import sys
import unittest


def run_cmd(cmd):
    """Run a command and return a tuple with (stdout, stderr, exit_code)"""
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
        (o, e, s) = run_cmd(sys.executable + ' app.py db init')
        self.assertTrue(s == 0)
        (o, e, s) = run_cmd(sys.executable + ' app.py db migrate')
        self.assertTrue(s == 0)
        (o, e, s) = run_cmd(sys.executable + ' app.py db upgrade')
        self.assertTrue(s == 0)
        (o, e, s) = run_cmd(sys.executable + ' app.py add')
        self.assertTrue(s == 0)

    def test_custom_directory(self):
        (o, e, s) = run_cmd(sys.executable + ' app_custom_directory.py db init')
        self.assertTrue(s == 0)
        (o, e, s) = run_cmd(sys.executable + ' app_custom_directory.py db migrate')
        self.assertTrue(s == 0)
        (o, e, s) = run_cmd(sys.executable + ' app_custom_directory.py db upgrade')
        self.assertTrue(s == 0)
        (o, e, s) = run_cmd(sys.executable + ' app_custom_directory.py add')
        self.assertTrue(s == 0)

    def test_custom_directory_path(self):
        (o, e, s) = run_cmd(sys.executable + ' app_custom_directory_path.py db init')
        self.assertTrue(s == 0)
        (o, e, s) = run_cmd(sys.executable + ' app_custom_directory_path.py db migrate')
        self.assertTrue(s == 0)
        (o, e, s) = run_cmd(sys.executable + ' app_custom_directory_path.py db upgrade')
        self.assertTrue(s == 0)
        (o, e, s) = run_cmd(sys.executable + ' app_custom_directory_path.py add')
        self.assertTrue(s == 0)

    def test_compare_type(self):
        (o, e, s) = run_cmd(sys.executable + ' app_compare_type1.py db init')
        self.assertTrue(s == 0)
        (o, e, s) = run_cmd(sys.executable + ' app_compare_type1.py db migrate')
        self.assertTrue(s == 0)
        (o, e, s) = run_cmd(sys.executable + ' app_compare_type1.py db upgrade')
        self.assertTrue(s == 0)
        (o, e, s) = run_cmd(sys.executable + ' app_compare_type2.py db migrate')
        self.assertTrue(s == 0)
        self.assertTrue(b'Detected type change from VARCHAR(length=128) '
                        b'to String(length=10)' in e)
