import sys
from datetime import datetime, timedelta
from sqlalchemy.sql.expression import and_

from deliver.converter import UnicodeMessage
from models import message, digest

import logging
logger = logging.getLogger('db')

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
    logger.info('Using %s module for the database', full_name)
    return sys.modules[full_name]

class Store:
    '''
    This class is responsible for interacting with the DB.

    It provides an interface that allows to archive messages, retrieve
    them, and also work with digests.

    It is implemented with a number of model classes that represent
    the tables in the DB. This model instances are generally not
    passed to the caller.
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
        logger.info('Connecting to %s:%s with user %s', self._cfg['name'], self._cfg['host'], self._cfg['user'])
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
        logger.info('Archiving message %s', m)
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
        logger.info('Marking message as sent %s', m)
        self._db.session.flush()

    def digest(self, msg_id, *recipients):
        '''
        For every recipient, stores a digest notification in the db
        for the given message.

        msg_id the id of the message for the digest

        *recipients the list of recipients of the digest

        It is important to note that this method cannot be used before
        a message has been store using the archive method.
        '''
        assert isinstance(msg_id, unicode)
        for recipient in recipients:
            assert isinstance(recipient, unicode)
        time = datetime.now()
        digests = [digest.Digest(msg_id, recipient, time) for recipient in recipients]
        logger.info('Creating digests %s', digests)
        self._db.session.add_all(digests)
        self._db.session.flush()

    def _pending_digests(self, recipient):
        '''
        Returns all the digests that are still pending for the given
        user.
        '''
        assert isinstance(recipient, unicode)
        return self._db.session.query(digest.Digest) \
            .filter(and_(digest.Digest.send_to==recipient, digest.Digest.sent_at==None)) \
            .all()

    def users_with_pending_digests(self):
        '''
        Returns a set with email addresses that have pending digests.
        '''
        digests = self._db.session.query(digest.Digest) \
            .filter(digest.Digest.sent_at==None) \
            .order_by(digest.Digest.scheduled_at) \
            .all()
        addresses = set(d.send_to for d in digests)
        logger.debug('users_with_pending_digests: %s', addresses)
        return addresses

    def messages_for_user(self, recipient):
        '''
        Returns all the messages which have a pending digest for the
        given user. The messages are returned as UnicodeMessage
        objects. They are ordered by the time at which they were
        scheduled.

        recipient the email address for the user
        '''
        digests = self._pending_digests(recipient)
        logger.debug('messages_for_user found digests for %s: %s', recipient, digests)
        return [d.msg.parsed_content for d in digests]

    def _mark_as_sent(self, digests):
        '''
        Mark the given digests as sent by setting the sent_at field
        with the current time.

        returns the list of ids of the messages that were set as sent
        '''
        time = datetime.now()
        for d in digests:
            d.sent_at = time
        self._db.session.flush()
        return [d.msg_id for d in digests]

    def mark_digest_as_sent(self, recipient):
        '''
        Marks all the open digests for the given user as sent.

        recipient the email address for the user whose digests are to
        be marked as sent.

        returns the list of ids of the messages that were set as sent
        '''
        digests = self._pending_digests(recipient)
        logger.debug('mark_digest_as_sent has digests for %s: %s', recipient, digests)
        return self._mark_as_sent(digests)

    def discard_old_digests(self, days):
        '''
        Marks old digests as sent.

        days the number of days for the cutoff. If it is for example
        3, all digests older than three days will be discarded.

        returns the list of ids of the messages that were set as sent
        '''
        cutoff = datetime.now() - timedelta(days=days)
        digests = self._db.session.query(digest.Digest) \
            .filter(and_(digest.Digest.sent_at==None, digest.Digest.scheduled_at < cutoff)) \
            .all()
        logger.debug('discard_old_digests is discarding: %s', digests)
        return self._mark_as_sent(digests)

    # DEBUG

    def connection(self):
        '''Gets a connection to the db that can run raw SQL. This
        method should be only used for debugging purposes'''
        return self._db.engine.connect()
