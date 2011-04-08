import unittest
from mock import patch
from deliver.send import Sender

class SenderTest(unittest.TestCase):

    def setUp(self):
        self.sender = Sender()

    @patch('smtplib.SMTP')
    def test_send(self, smtp):
        self.sender.send_new('test mail', 'content', 'email@address.com')
