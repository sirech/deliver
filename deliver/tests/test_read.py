import unittest
from test_base import BaseTest
from mock import patch, Mock

from poplib import POP3
from deliver.read import Reader

class ReaderTest(BaseTest):

    def setUp(self):
        super(ReaderTest,self).setUp()
        self.reader = Reader(self.config)

    @patch('poplib.POP3')
    @patch.object(POP3, 'user')
    @patch.object(POP3, 'pass_')
    def test_connect(self, pop3, user, pwd):
        self.reader.connect()

        # self.assertEqual(user.call_count, 1)
        self.assertEqual(pwd.call_count, 1)

    @patch('poplib.POP3')
    @patch.object(POP3, 'quit')
    def test_disconnect(self, pop3, disc):
        self.reader.connect()
        self.reader.disconnect()

        self.assertEqual(disc.call_count, 1)

