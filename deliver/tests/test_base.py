import os
import unittest
import email

from deliver.converter import UnicodeMessage
from deliver.db.models import message

def load_msg(fileName):
    '''Loads the message contained in the given file and returns it as
    an UnicodeMessage.'''
    return UnicodeMessage(email.message_from_file(open('test_data/%s' % fileName)))

def load_all_msg():
    '''Loads all the available sample messages and returns them as a list.'''
    return [load_msg(fileName) for fileName in ['sample', 'sample2',
                                                'sample3',
                                                'sample4', # content base64
                                                'sample5', # content base64 utf-8
                                                'sample6', # empty content
                                                'sample7', # invalid sender
                                                'sample8', # whitelisted sender
                                                ]]

def get_msg(store, id):
    '''
    Retrieve a message from the db.

    store the store object to use to get a connection to the db.

    id the value of the Message-Id header that is used to uniquely
    identify a message.
    '''
    return store._db.session.query(message.Message).get(id)

class BaseTest(unittest.TestCase):

    def setUp(self):
        from test_data.test_config import py
        self.config = py

    def tearDown(self):
        super(BaseTest,self).tearDown()
        if os.path.isfile(self.config['db_name']):
            os.remove(self.config['db_name'])
