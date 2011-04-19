# -*- coding: utf-8 -*-
from test_base import BaseTest, load_msg, get_msg
from mock import Mock

from deliver.distribute import OfflineDistributor
from deliver.send import Sender

class OfflineDistributeTest(BaseTest):

    def setUp(self):
        super(OfflineDistributeTest,self).setUp()
        self.distributor = OfflineDistributor(self.config)
        self.sender = Mock(spec=Sender)
        self.distributor._sender = self.sender
        self.msg = load_msg('sample')

    def test_update_nothing_new(self):
        self.assertFalse(self.distributor.update())
        self.assertEqual(self.sender.send.call_count, 0)
