import os
import unittest
import email

from deliver.converter.simple import UnicodeMessage
from deliver.db.models import message, digest

def open_data(fileName):
    '''
    Opens the given file, which resides in the folder where all the
    test data is.
    '''
    return open(os.path.join('test_data', fileName))

def load_msg(fileName):
    '''Loads the message contained in the given file and returns it as
    an UnicodeMessage.'''
    return UnicodeMessage(email.message_from_file(open_data(fileName)))

def load_all_msg():
    '''Loads all the available sample messages and returns them as a list.'''
    return [load_msg(fileName) for fileName in ['sample', 'sample2',
                                                'sample3',
                                                'sample4', # content base64
                                                'sample5', # content base64 utf-8
                                                'sample6', # empty content
                                                'sample7', # invalid sender
                                                'sample8', # whitelisted sender
                                                'sample9',  # blacklisted sender
                                                'sample10', # get www.google.com
                                                'sample11', # no header/body encoding
                                                'sample13', # msg without subject
                                                ]]

def get_msg(store, id):
    '''
    Retrieve a message from the db.

    store the store object to use to get a connection to the db.

    id the value of the Message-Id header that is used to uniquely
    identify a message.
    '''
    return store._db.session.query(message.Message).get(id)

def archive_msg(store, fileName, *addresses):
    '''
    Archives the message contained in the given file.

    store the store object to use to get a connection to the db

    fileName the name of the file where the message to archive is
    contained

    *addresses the list of email addresses for which a digest should
    be produced

    Returns a tuple in the form (id, msg).
    '''
    msg = load_msg(fileName)
    store.archive(msg)
    store.digest(msg.id, *addresses)
    return (msg.id, msg)

def get_digests(store, address):
    '''
    Retrieve all the digests for the given address.

    address the email address whose digests are to be retrieved.
    '''
    return store._db.session.query(digest.Digest).filter(digest.Digest.send_to==address)

class BaseTest(unittest.TestCase):

    def setUp(self):
        from test_data.test_config import py
        self.config = py

    def tearDown(self):
        super(BaseTest,self).tearDown()
        if os.path.isfile(self.config['db_name']):
            os.remove(self.config['db_name'])
