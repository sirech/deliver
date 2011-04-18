import sys
from datetime import datetime

from deliver.converter import UnicodeMessage
from deliver.db.models import message

DB = {
    'sqlite' : 'sqlite'
    }

def choose_backend(backend_name):
    '''
    Imports the module that can work with the specified backend.

    backend_name the entry in the DB map with the name of the module
    to be used to work with the db.

    Returns the imported module.
    '''
    full_name = 'deliver.db.%s' % DB[backend_name]
    __import__(full_name)
    return sys.modules[full_name]

class Store:
    '''
    This class is responsible for storing messages in a DB.
    '''

    def __init__(self, config):
        '''
        Creates a new instance of the object. Also initializes the
        connection to the db.

        config the configuration object which contains the connection data for the DB.
        '''
        self._cfg = {}
        for key in ['type', 'host', 'name', 'user', 'password']:
            self._cfg[key] = config['db_%s' % key]
        self._init_db()

    def _init_db(self):
        '''
        Initializes the db.

        It does so by calling the choose_backend method with the type
        of the db specified in the config file. This provides the
        module that can be used to communicate with it.
        '''
        module = choose_backend(self._cfg['type'])
        self._db = module.DBWrapper(**self._cfg)

    def archive(self, msg):
        '''
        Stores a message in the db. It sets the received time with the
        current time.

        msg the message to store. It is stored as a string, using the
        Message-Id header as the key.

        Returns the id used for the entry.
        '''
        assert isinstance(msg, UnicodeMessage)
        m = message.Message(msg['Message-Id'], msg, datetime.now())
        self._db.session.add(m)
        self._db.session.flush()
        return m.id

    def mark_as_sent(self, msg_id):
        '''
        Marks a message as sent, by setting the sent time with the
        current time.

        msg_id the id of the message to modify.
        '''
        assert isinstance(msg_id, unicode)
        m = self._db.session.query(message.Message).get(msg_id)
        assert m.sent_at is None
        m.sent_at = datetime.now()
        self._db.session.flush()

    def connection(self):
        '''Gets a connection to the db that can run raw SQL. This
        method should be only used for debugging purposes'''
        return self._db.engine.connect()
