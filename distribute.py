import json
import re
import random
import logging
import logging.config

from send import Sender
from read import Reader

logging.config.fileConfig("logging.conf")
logging.getLogger('distribute')

BASIC_EMAIL = re.compile(r'<(.+@.+\..+)>')

class Distributor:

    def __init__(self):
        self._sender = Sender()
        self._reader = Reader()
        self._mgr = MemberMgr()
        self._cfg = json.load(open('configuration.json'))
        self._manifest = json.load(open('manifest.json'))

    def update(self):
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
        self._edit_msg(msg)
        self._sender.send(msg, *self._mgr.active_members(self._find_sender_email(msg)))

    def _isvalid(self, msg):
        return True

    def _find_sender_email(self, msg):
        candidates = [ msg['From'], msg['Return-Path']]
        for candidate in candidates:
            match = BASIC_EMAIL.search(candidate)
            if match and len(match.groups()) == 1:
                logging.debug('_find_sender_email found %s' % match.groups())
                return match.group(1).lower()
        logging.debug('_find_sender_email did not find the email in %s' % candidates)
        return ''

    def _edit_msg(self, msg):
        header = self._add_header(msg)
        footer = self._add_footer(msg)
        for editable in self._find_actual_text(msg):
            charset = editable.get_content_charset()
            nl = '\n' if editable.get_content_subtype() == 'plain' else '<br>'
            editable.set_payload((nl * 2).join([
                        nl.join(header).encode(charset, errors='ignore'),
                        EMAIL.sub(anonymize_email, editable.get_payload()),
                        nl.join(footer).encode(charset, errors='ignore')]))

    def _find_actual_text(self, msg):
        for part in msg.walk():
            if 'text' == part.get_content_maintype():
                yield part

    def _add_header(self, msg):
        member = self._mgr.find_member(self._find_sender_email(msg))
        if member is not None:
            header = self._mgr.choose_name(member) + ' ' + self._choose_intro() + ':'
            logging.debug('_add_header produced: %s' % header)
            return [header]
        return ['']

    def _choose_intro(self):
        return random.choice(self._cfg['introductions'])

    def _add_footer(self, msg):
        return ['_' * 60,
                self._cfg['real_name'],
                random.choice(self._cfg['quotes']),
                self._powered_by()]

    def _powered_by(self):
        name = self._manifest['name']
        version = self._manifest['version']
        description = self._manifest['description']
        return 'Powered by %s %s, %s' % (name, version, description)

EMAIL = re.compile(r'@([a-zA-Z0-9.-]+\.\w{2,3})')

def anonymize_email(match):
    chars = 'abcdefghijklmnopqrstuvwxyz'
    replacement = ''
    for i in range(len(match.group(1))):
        replacement += random.choice(chars)
    return '@%s' % replacement

class MemberMgr:

    def __init__(self):
        self._members = self._members = json.load(open('members.json'))


    def active_members(self, sender = ''):
        sender = sender.lower()
        return [member['email'] for member in self._members['members']
                if member['active'] and member['email'] != sender]

    def find_member(self, email):
        for member in self._members['members']:
            if member['email'].lower() in email:
                logging.debug('find_member found %s' % member)
                return member
        logging.error('find_member for %s had no results' % email)
        return None

    def iswhitelisted(self, addr):
        return addr.lower() in self._members['whitelist']

    def choose_name(self, member):
        if member.has_key('aliases'):
            return random.choice([member['name']] + member['aliases'])
        return member['name']

if __name__ == '__main__':
    d = Distributor()
    d.update()
