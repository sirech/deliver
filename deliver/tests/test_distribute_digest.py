# -*- coding: utf-8 -*-
from test_base import BaseTest, load_msg, get_msg, archive_msg
from mock import Mock

from deliver.distribute import OfflineDistributor
from deliver.send import Sender

class OfflineDistributeTest(BaseTest):

    def setUp(self):
        super(OfflineDistributeTest,self).setUp()
        self.distributor = OfflineDistributor(self.config)
        self.sender = Mock(spec=Sender)
        self.distributor._sender = self.sender
        self.store = self.distributor._store
        self.msg = load_msg('sample')

    def test_update_nothing_new(self):
        self.assertFalse(self.distributor.update())
        self.assertEqual(self.sender.send.call_count, 0)

    def _test_update(self, fileList, *addresses):
        for f in fileList:
            archive_msg(self.store, f, *addresses)

        self.assertTrue(self.distributor.update())

        for user in addresses:
            self.assertEqual(self.store.messages_for_user(user), [])
        self.assertEqual(self.sender.send.call_count, len(addresses))

    def test_update_one_msg_one_addr(self):
        self._test_update(['sample'], u'test@mail.com')

    def test_update_one_msg_multiple_addr(self):
        self._test_update(['sample2'], u'test@mail.com',  u'external@mail.com')

    def test_update_multiple_msg_one_addr(self):
        self._test_update(['sample3', 'sample4' ], u'test@mail.com')

    def test_update_multiple_msg_multiple_addr(self):
        self._test_update(['sample5', 'sample7' ], u'test@mail.com',  u'external@mail.com')
