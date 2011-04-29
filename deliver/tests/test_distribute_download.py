# -*- coding: utf-8 -*-
from test_base import BaseTest, load_msg, open_data
from test_distribute import check_start_stop, check_interactions, check_archived
from mock import patch, Mock

from deliver.distribute import OnlineDistributor
from deliver.read import Reader
from deliver.send import Sender

class OnlineDownloadDistributeTest(BaseTest):

    def setUp(self):
        super(OnlineDownloadDistributeTest,self).setUp()
        self.distributor = OnlineDistributor(self.config)
        self.sender = Mock(spec=Sender)
        self.distributor._sender = self.sender
        self.reader = Mock(spec=Reader)
        self.distributor._reader = self.reader
        self.msg = load_msg('sample10')

    def test_get_download_url(self):
        self.assertEqual(self.distributor._get_download_url(u'GET http://www.google.com'), u'http://www.google.com')

    def test_get_download_url_extra_whitespace(self):
        self.assertEqual(self.distributor._get_download_url(u'   GET    http://www.google.com    '),
                         u'http://www.google.com')

    def test_get_download_url_too_few_args(self):
        self.assertEqual(self.distributor._get_download_url(u'http://www.google.com'), None)

    def test_get_download_url_too_many_args(self):
        self.assertEqual(self.distributor._get_download_url(u'GET http://www.google.com plus'), None)

    @patch('urllib2.urlopen')
    def test_update(self, urlopen):
        urlopen.return_value = open_data('google.html')
        self.reader.new_messages.return_value = [1237]
        self.reader.get.return_value = self.msg
        self.assertTrue(self.distributor.update())

        check_start_stop(self)
        check_interactions(self, 1237)
        check_archived(self, self.msg)

    def test_update_invalid_url(self):
        self.reader.new_messages.return_value = [1237]
        self.reader.get.return_value = self.msg
        self.msg.replace_header('Subject', u'GET')
        self.assertTrue(self.distributor.update())

        check_start_stop(self)
        self.assertEqual(self.sender.send.call_count, 0)
        self.assertEqual(self.reader.delete.call_count, 1)
