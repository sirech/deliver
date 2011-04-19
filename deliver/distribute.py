import json
import re
import random
import logging
import logging.config

from send import Sender
from read import Reader
from members import MemberMgr
from db.store import Store

logging.config.fileConfig("logging.conf")
logging.getLogger('distribute')

BASIC_EMAIL = re.compile(r'<(.+@.+\..+)>')

class Distributor:
    '''
    This class is responsible for distributing mails to the members of the list, making sure
    the right members get mails and processing the mails according to the configuration.

    There is one public method, update. When it is called, the server is polled. If new mails have
    arrived, they are processed and resent to the members of the list. Afterward, the mails
    are deleted, but only if the resend process finished successfully.

    Most options are configurable via json configuration files.
    '''

    def __init__(self, config):
        self._sender = Sender(config)
        self._reader = Reader(config)
        self._mgr = MemberMgr(config)
        self._store = Store(config)
        self._cfg = config
        self._manifest = json.load(open('manifest.json'))

    def update(self):
        '''
        Update the distribution list. Every new message in the server is processed and resent to the
        members of the list. If the resend is successful the new messages are deleted.
        '''
        logging.debug('update is called')
        self._reader.connect()
        ids = self._reader.new_messages()
        for id in ids:
            msg = self._reader.get(id)
            if self._isvalid(msg):
                self._resend(msg)
                self._reader.delete(id)
        self._reader.disconnect()
        logging.debug('update is finished')
        return len(ids) != 0

    def _resend(self, msg):
        '''
        Sends a message to the appropriate members of the list after processing it.
        '''
        self._edit_msg(msg)
        id = self._store.archive(msg)
        sender = self._find_sender_email(msg)
        self._sender.send(msg, *self._mgr.active_members(sender))
        self._store.digest(id, *self._mgr.digest_members(sender))
        self._store.mark_as_sent(id)

    def _isvalid(self, msg):
        '''Checks if the message can be delivered.'''
        email = self._find_sender_email(msg)
        if self._mgr.isblacklisted(email):
            return False
        return self._mgr.find_member(email) is not None or self._mgr.iswhitelisted(email)

    def _find_sender_email(self, msg):
        '''
        Finds the email of the sender of the given message. The *From* and *Return-Path* headers
        from the message are searched. An empty string is returned in case the email
        cannot be found.
        '''
        candidates = [ msg['From'], msg['Return-Path']]
        for candidate in candidates:
            match = BASIC_EMAIL.search(candidate)
            if match and len(match.groups()) == 1:
                logging.debug('_find_sender_email found %s' % match.groups())
                # Normalize
                return match.group(1).lower()
        logging.debug('_find_sender_email did not find the email in %s' % candidates)
        return ''

    def _edit_msg(self, msg):
        '''
        Processes a message and returns it. The following steps are taken for each part of the
        message that can be interpreted as text:

        - A header and a footer are added, both using the encoding of the payload.
        - The payload has all the email hosts removed.

        The parts are separated with newlines, which depend on whether the message is plain text or
        other (like HTML).
        '''
        header = self._create_header(msg)
        footer = self._create_footer(msg)
        for editable in self._find_actual_text(msg):
            nl = u'\n' if editable.get_content_subtype() == 'plain' else u'<br>'
            editable.set_payload((nl * 2).join([
                        nl.join(header),
                        EMAIL.sub(anonymize_email, editable.get_payload(decode=True)),
                        nl.join(footer)]))

    def _find_actual_text(self, msg):
        '''Yields all the parts of the message that can be interpreted as text.'''
        for part in msg.walk():
            if 'text' == part.get_content_maintype():
                yield part

    def _create_header(self, msg):
        '''
        Creates a header for the message, returned as a list of strings. The header contains the
        name of the sender and an introduction message.
        '''
        member = self._mgr.find_member(self._find_sender_email(msg))
        if member is not None:
            header = self._mgr.choose_name(member) + ' ' + self._choose_intro() + ':'
            logging.debug('_create_header produced: %s' % header)
            return [header]
        return ['']

    def _choose_intro(self):
        '''Randomly chooses an introduction text from the configuration.'''
        return random.choice(self._cfg['introductions'])

    def _create_footer(self, msg):
        '''
        Creates a footer for the message, returned as a list of strings. The footer contains the
        name of the list, a randomly chosen quote and the program id.
        '''
        return [u'_' * 60,
                self._cfg['real_name'],
                random.choice(self._cfg['quotes']),
                self._powered_by()]

    def _powered_by(self):
        '''
        Returns the program id, which consists of the name, version, and description of this sw.
        '''
        name = self._manifest['name']
        version = self._manifest['version']
        description = self._manifest['description']
        return u'Powered by %s %s, %s' % (name, version, description)

# Identify the host in an email
EMAIL = re.compile(r'@([a-zA-Z0-9.-]+\.\w{2,3})')

def anonymize_email(match):
    '''
    Replaces the host of an email identified by the EMAIL regexp. The replacement is of the same
    length, and consists of random letters.
    '''
    chars = 'abcdefghijklmnopqrstuvwxyz'
    replacement = ''.join(random.choice(chars) for i in range(len(match.group(1))))
    logging.debug('replacing %s with %s' % (match.group(1), replacement))
    return u'@%s' % replacement
