import unittest
from test_base import BaseTest
from mock import patch, Mock

from smtplib import SMTP
from deliver.send import Sender

class SenderTest(BaseTest):

    def setUp(self):
        super(SenderTest,self).setUp()
        self.sender = Sender()

    @patch('smtplib.SMTP')
    @patch.object(SMTP, 'sendmail')
    def test_send(self, smtp, sendmail):
        self.sender.send_new('test mail', 'content', 'email@address.com')

        self.assertEqual(sendmail.call_count, 1)

        print sendmail.call_args
        # self.assertEqual(smtp.quit.call_count, 1)

    def test_get_address(self):
        self.assertEqual(self.sender.get_address(),self.config['sender'])

