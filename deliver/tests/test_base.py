import unittest
import email

def load_msg(fileName):
    '''Loads the message contained in the given file and returns it as
    an email.'''
    return email.message_from_file(open('test_data/%s' % fileName))

class BaseTest(unittest.TestCase):

    def setUp(self):
        from test_data.test_config import py
        self.config = py
