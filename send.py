import smtplib
import json
from mail_builder import create_msg

class Sender:

    def __init__(self):
        self._credentials = self.load_credentials('credentials.json')

    def send(self, content, recipients):
        msg = create_msg(self.get_address(), 'test', 'some message')
        s = smtplib.SMTP('localhost')
        for recipient in recipients:
            msg['To'] = recipient
            s.sendmail(self.get_address(), recipient, msg.as_string())
            s.quit()

    def load_credentials(self, filename):
        return json.load(open(filename))

    def get_address(self):
        return self._credentials['sender']
