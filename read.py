import poplib
import email
import json
import logging
import logging.config

logging.config.fileConfig("logging.conf")
logging.getLogger('distribute')

class Reader:
    '''
    Class that is responsible for receiving/deleting mails from a specified POP3 account.

    To use the methods of this class, it is necessary to call the connect method beforehand.
    After finishing with the processing, it is recommended to call the disconnect method. Otherwise,
    updates to the underlying mail account, such as new messages, will be missed. Deleted messages
    are not really deleted until the disconnection, either.
    '''

    def __init__(self):
        self._creds = json.load(open('credentials.json'))
        self._cfg = json.load(open('configuration.json'))


    def connect(self):
        '''Connects to the server, which allows the other methods to be called.'''
        self._s = poplib.POP3(self._creds['pop_server'])
        self._check(self._s.user(self._creds['sender']))
        self._check(self._s.pass_(self._creds['password']))

    def disconnect(self):
        '''Disconnects from the server, committing the changes.'''
        self._check(self._s.quit())

    def new_messages(self):
        '''
        Gets a list of the ids (ints) of the new messages in the server,
        sorted by ascending order.
        '''
        st, msg_list, _ = self._s.list()
        self._check(st)
        logging.debug('new_messages: %s' % msg_list)
        return sorted(int(msg.split(' ')[0]) for msg in msg_list)

    def get(self, id):
        '''Gets the message identified by the given id as a email object.'''
        st, lines, _ = self._s.retr(id)
        self._check(st)
        return email.message_from_string('\n'.join(lines))

    def delete(self, id):
        '''Marks the message identified by the given id for removal.'''
        self._check(self._s.dele(id))

    def _check(self, st):
        '''
        Checks the given return code. If there is an error, it is logged and a message is sent
        to a debug address, if one exists.
        '''
        if not st.startswith('+OK') and 'debug' in self._creds:
            logging.error('failed operation: %s' % st)
            from send import Sender
            snd = Sender()
            snd.send_new('DEBUG', st, self._creds['debug'])
