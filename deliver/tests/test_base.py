import unittest

class BaseTest(unittest.TestCase):

    def setUp(self):
        self.config = {
            'sender' : 'test@test.com',
            'smtp_server' : 'localhost',
            'pop_server' : 'mail.test.com',
            'password' : 'abcdef',
            'subject_prefix' : u'[Test]',
            'introductions' : [u'says', u'tells'],
            'quotes' : [u'No quote', u'No quote 2'],
            'real_name' : u'Test',
            'members' : 'members.json.example'
            }
