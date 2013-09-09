import os
import shutil
from exceptions import OSError
import unittest

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

        os.system('python app.py db init')
        os.system('python app.py db migrate')
        os.system('python app.py db upgrade')

    def tearDown(self):
        try:
            os.remove('app.db')
        except OSError:
            pass
        try:
            shutil.rmtree('migrations')
        except OSError:
            pass

    def test_migrate_upgrade(self):
        from app import db, User
        db.session.add(User(name = 'test'))
        db.session.commit()

if __name__ == '__main__':
    unittest.main()

