import poplib
import email

class Reader:

    def __init__(self):
        self._creds = self.load_json('credentials.json')
        self._cfg = self.load_json('configuration.json')


    def connect(self):
        self._s = poplib.POP3(self._creds['pop_server'])
        self.check(self._s.user(self._creds['sender']))
        self.check(self._s.pass_(self._creds['password']))

    def disconnect(self):
        self.check(self._s.quit())

    def new_messages(self):
        st, msg_list, _ = self._s.list()
        self.check(st)
        return [msg.split('')[0] for msg in msg_list]

    def get(self, id):
        st, lines, _ = self._s.retr(id)
        self.check(st)
        return email.message_from_string('\n'.join(lines))

    def delete(self, id):
        self.check(self._s.dele(id))

    def check(self, st):
        if not st.startswith('+OK') and 'debug' in self._creds:
            from send import Sender
            snd = Sender()
            snd.send('DEBUG', st, self._creds['debug'])
