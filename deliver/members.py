import json
import random
import codecs

import logging
logging.getLogger(__name__)

class MemberMgr:
    '''
    Class that is responsible of dealing with the members of the list.

    The members are stored as a json file. An example is found in the
    members.json.example file.
    '''

    def __init__(self, config):
        self._members = json.load(codecs.open(config['members'], 'r', 'utf-8'))

    def _choose_email_address(self, member) :
        '''
        Chooses an email address from the mail hash for the given
        member, by using the send_to key. If the key is not defined
        for the member, default is used as the key.'''
        send_to = member['send_to'] if member.has_key('send_to') else 'default'
        return member['email'][send_to]

    def _member_query(self, exclude = u'', active=True, digest=False):
        '''
        Returns a generator will all the members that fulfill the given conditions.

        optional exclude the address that should not appear in the results

        optional active whether the user should be active or not

        optional digest whether the user should receive messages as a digest or not

        If a member does not contain one of the attributes used for
        the query (active, digest), it is considered to have a False
        value.
        '''
        # Normalize
        exclude = exclude.lower()
        return (self._choose_email_address(member) for member in self._members['members']
                if member.get('active', False) is active and member.get('digest', False) is digest
                and not self._is_email_for_member(member, exclude))

    def active_members(self, sender = u''):
        '''
        Returns a list with the email addresses of all the active
        members of the list, as unicode strings. Users in digest mode
        are excluded.

        Optional sender the sender, who should be excluded from the
        results.
        '''
        return list(self._member_query(exclude=sender))

    def digest_members(self, sender = u''):
        '''
        Returns a list with the email addresses of all the active
        members of the list that are also digest users, as unicode
        strings.

        Optional sender the sender, who should be excluded from the
        results.
        '''
        return list(self._member_query(exclude=sender, digest=True))

    def _is_email_for_member(self, member, email):
        '''
        Returns true if the given email is one of the defined mails
        for the given member, and false otherwise.
        '''
        for m in member['email'].values():
            if m.lower() in email:
                return True
        return False

    def find_member(self, email):
        '''
        Returns the member with the given email address, or None if
        there is not one.
        '''
        # Normalize
        email = email.lower()
        try:
            member = (m for m in self._members['members']
                      if self._is_email_for_member(m,email)).next()
        except StopIteration:
            logging.error('find_member for %s had no results', email)
            return None
        logging.debug('find_member found %s', member)
        return member

    def iswhitelisted(self, addr):
        '''Checks if the given email address appears in the
        whitelist.'''
        return addr.lower() in self._members['whitelist']

    def isblacklisted(self, addr):
        '''Checks if the given email address appears in the
        blacklist.'''
        return addr.lower() in self._members['blacklist']

    def choose_name(self, member):
        '''Randomly chooses a name for the given member, between her
        name and aliases.'''
        if member.has_key('aliases'):
            return random.choice([member['name']] + member['aliases'])
        return member['name']
