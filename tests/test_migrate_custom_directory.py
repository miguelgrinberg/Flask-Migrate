import os
import shutil
from exceptions import OSError
import unittest

class TestMigrate(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.split(os.path.abspath(__file__))[0])
        try:
            os.remove('app2.db')
        except OSError:
            pass
        try:
            shutil.rmtree('temp_folder')
        except OSError:
            pass

        os.system('python app2.py db init')
        os.system('python app2.py db migrate')
        os.system('python app2.py db upgrade')

    def tearDown(self):
        try:
            os.remove('app2.db')
        except OSError:
            pass
        try:
            shutil.rmtree('migrations')
        except OSError:
            pass

    def test_migrate_upgrade(self):
        from app2 import db, User
        db.session.add(User(name = 'test'))
        db.session.commit()

if __name__ == '__main__':
    unittest.main()

