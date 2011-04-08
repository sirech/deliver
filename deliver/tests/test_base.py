import unittest

class BaseTest(unittest.TestCase):

    def setUp(self):
        self.config = {
            'sender' : 'test@test.com',
            'smtp_server' : 'localhost',
            'pop_server' : 'mail.test.com'
            }
