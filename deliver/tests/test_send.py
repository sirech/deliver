from test_base import BaseTest, load_msg
from mock import patch

from smtplib import SMTP

from deliver.send import Sender
from deliver.converter import UnicodeMessage

class SendTest(BaseTest):

    def setUp(self):
        super(SendTest,self).setUp()
        self.sender = Sender(self.config)

    @patch('smtplib.SMTP')
    @patch.object(SMTP, 'sendmail')
    def test_send(self, smtp, sendmail):
        msg = UnicodeMessage(load_msg('sample'))
        self.sender.send(msg, u'email@address.com')

        self.assertEqual(sendmail.call_count, 1)
        self.assertEqual(msg['To'], u'email@address.com')
        self.assertEqual(msg['From'], self.sender.get_address())
        self.assertEqual(msg['Subject'], u'[Test] BETA 2.0')

    def test_get_address(self):
        self.assertEqual(self.sender.get_address(),self.config['sender'])

