import json

from send import Sender
from read import Reader

class Distributor:

    def __init__(self):
        self._sender = Sender()
        self._reader = Reader()
        self._mgr = MemberMgr()

    def update(self):
        self._reader.connect()
        ids = self._reader.new_messages()
        for id in ids:
            self.resend(self._reader.get(id))
            self._reader.delete(id)
        self._reader.disconnect()

    def resend(self, msg):
        self._sender.send(msg, *self._mgr.members())

class MemberMgr:

    def __init__(self):
        self._members = self._members = json.load(open('members.json'))


    def members(self, sender = ''):
        sender = sender.lower()
        return [member['email'] for member in self._members['members']
                if member['active'] and member['email'] != sender]

if __name__ == '__main__':
    d = Distributor()
    d.update()
