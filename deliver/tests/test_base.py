import unittest
import email

def load_msg(fileName):
    '''Loads the message contained in the given file and returns it as
    an email.'''
    return email.message_from_file(open('test_data/%s' % fileName))

def load_all_msg():
    '''Loads all the available sample messages and returns them as a list.'''
    return [load_msg(fileName) for fileName in ['sample', 'sample2', 'sample3']]

class BaseTest(unittest.TestCase):

    def setUp(self):
        from test_data.test_config import py
        self.config = py
