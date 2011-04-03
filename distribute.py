import json
import re
import random
import logging
import logging.config

from send import Sender
from read import Reader

logging.config.fileConfig("logging.conf")
logging.getLogger('distribute')

class Distributor:

    def __init__(self):
        self._sender = Sender()
        self._reader = Reader()
        self._mgr = MemberMgr()
        self._cfg = json.load(open('configuration.json'))

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
        self._sender.send(msg, *self._mgr.members(self._find_sender_email(msg)))

    def _isvalid(self, msg):
        return True

    def _find_sender(self, msg):
        email = self._find_sender_email(msg)
        for member in self._members['members']:
            if member['email'] in email:
                logging.debug('_find_sender found %s' % member)
                return member
        logging.error('_find_sender for %s had no results' % email)
        return None

    def _find_sender_email(self, msg):
        pattern = re.compile(r'<(.*?@.*?\..*?)>')
        candidates = [ msg['From'], msg['Return-Path']]
        for candidate in candidates:
            match = pattern.search(candidate)
            if match and len(match.groups()) == 1:
                logging.debug('_find_sender_email found %s' % match.groups())
                return match.group(1).lower()
        logging.debug('_find_sender_email did not find the email in %s' % candidates)
        return ''

    def _edit_msg(self, msg):
        editable = self._find_actual_text(msg)
        if editable is not None:
            editable._payload = self._add_header(msg) + editable._payload + self._add_footer(msg)

    def _find_actual_text(self, msg):
        for part in msg.walk():
            if part.get_content_type() == 'text':
                return part
        logging.error('could not find the text of the message')
        return None

    def _add_header(self, msg):
        member = self._find_sender(msg)
        if member is not None:
            header = self._mgr.choose_name(member) + ' ' + self._choose_intro() + ':'
            logging.debug('_add_header produced: %s' % header)
            return header
        return ''

    def _choose_intro(self):
        return random.choice(self._cfg['introductions'])

    def _add_footer(self, msg):
        return ''

class MemberMgr:

    def __init__(self):
        self._members = self._members = json.load(open('members.json'))


    def members(self, sender = ''):
        sender = sender.lower()
        return [member['email'] for member in self._members['members']
                if member['active'] and member['email'] != sender]

    def iswhitelisted(self, addr):
        return addr.lower() in self._members['whitelist']

    def choose_name(self, member):
        if member.has_key('aliases'):
            return random.choice([member['name']] + member['aliases'])
        return member['name']

if __name__ == '__main__':
    d = Distributor()
    d.update()
