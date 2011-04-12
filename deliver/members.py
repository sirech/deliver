import json
import random

import logging
import logging.config

logging.config.fileConfig("logging.conf")
logging.getLogger('distribute')

class MemberMgr:
    '''
    Class that is responsible of dealing with the members of the list.

    The members are stored as a json file. An example is found in the
    members.json.example file.
    '''

    def __init__(self, config):
        self._members = self._members = json.load(open(config['members']))

    def active_members(self, sender = ''):
        '''
        Returns the email addresses of all the active members of the
        list, except of the sender, if one is given.
        '''
        # Normalize
        sender = sender.lower()
        return [member['email'] for member in self._members['members']
                if member['active'] and member['email'] != sender]

    def find_member(self, email):
        '''
        Returns the member with the given email address, or None if
        there is not one.
        '''
        # Normalize
        email = email.lower()
        for member in self._members['members']:
            if member['email'].lower() in email:
                logging.debug('find_member found %s' % member)
                return member
        logging.error('find_member for %s had no results' % email)
        return None

    def iswhitelisted(self, addr):
        '''Checks if the given email address appears in the
        whitelist.'''
        return addr.lower() in self._members['whitelist']

    def choose_name(self, member):
        '''Randomly chooses a name for the given member, between her
        name and aliases.'''
        if member.has_key('aliases'):
            return random.choice([member['name']] + member['aliases'])
        return member['name']