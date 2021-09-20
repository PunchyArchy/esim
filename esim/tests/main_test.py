from esim.main import ESIMSignall, ESIMASU
import unittest
import os


class MainTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dbname = os.environ.get('DATABASE_NAME')
        self.dbuser = os.environ.get('DATABASE_USERNAME')
        self.dbpass = os.environ.get('DATABASE_PASSWORD')
        self.dbhost = os.environ.get('DATABASE_HOST')

    def test_ESIMSignall(self):
        inst = ESIMSignall('SignAll', 9, self.dbname, self.dbuser, self.dbpass,
                           self.dbhost)
        print(inst.main())

    def test_ESIMASU(self):
        inst = ESIMASU(9, self.dbname, self.dbuser, self.dbpass, self.dbhost)
        inst.main()
