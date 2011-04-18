import os

from deliver.tests.test_base import BaseTest, load_msg
from deliver.db.store import Store

class StoreTest(BaseTest):

    def setUp(self):
        super(StoreTest,self).setUp()
        self.store = Store(self.config)

    def tearDown(self):
        super(StoreTest,self).tearDown()
        os.remove(self.config['db_name'])

    def test_archive(self):
        self.store.archive(load_msg('sample'))

