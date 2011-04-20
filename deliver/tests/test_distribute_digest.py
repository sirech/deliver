# -*- coding: utf-8 -*-
from test_base import BaseTest, load_msg, get_msg, archive_msg, get_digests
from mock import Mock
from datetime import datetime, timedelta

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

    def _test_update_no_msgs(self):
        self.assertFalse(self.distributor.update())
        self.assertEqual(self.sender.send.call_count, 0)

    def test_update_nothing_new(self):
        self._test_update_no_msgs()

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

    def test_update_old_msgs(self):
        address = u'test@mail.com'
        archive_msg(self.store, 'sample8', address)
        get_digests(self.store, address)[0].scheduled_at = datetime.now() - timedelta(days=100)
        self.store._db.session.flush()

        self._test_update_no_msgs()

    def test_update_done_msgs(self):
        address = u'test@mail.com'
        archive_msg(self.store, 'sample9', address)
        self.store.mark_digest_as_sent(address)

        self._test_update_no_msgs()
