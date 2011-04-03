import poplib
import email
import json
import logging
import logging.config

logging.config.fileConfig("logging.conf")
logging.getLogger('distribute')

class Reader:

    def __init__(self):
        self._creds = json.load(open('credentials.json'))
        self._cfg = json.load(open('configuration.json'))


    def connect(self):
        self._s = poplib.POP3(self._creds['pop_server'])
        self.check(self._s.user(self._creds['sender']))
        self.check(self._s.pass_(self._creds['password']))

    def disconnect(self):
        self.check(self._s.quit())

    def new_messages(self):
        st, msg_list, _ = self._s.list()
        self.check(st)
        logging.debug('new_messages: %s' % msg_list)
        return sorted(int(msg.split(' ')[0]) for msg in msg_list)

    def get(self, id):
        st, lines, _ = self._s.retr(id)
        self.check(st)
        return email.message_from_string('\n'.join(lines))

    def delete(self, id):
        self.check(self._s.dele(id))

    def check(self, st):
        if not st.startswith('+OK') and 'debug' in self._creds:
            logging.error('failed operation: %s' % st)
            from send import Sender
            snd = Sender()
            snd.send_new('DEBUG', st, self._creds['debug'])
