from deliver.tests.test_base import BaseTest
from deliver.db.sqlite import DBWrapper

class SQLiteTest(BaseTest):

    def setUp(self):
        super(SQLiteTest,self).setUp()
        self.db = DBWrapper()

    def test_s(self):
        pass
