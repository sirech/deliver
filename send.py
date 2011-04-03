import smtplib
import json

from email.mime.text import MIMEText

class Sender:

    def __init__(self):
        self._credentials = self.load_json('credentials.json')
        self._cfg = self.load_json('configuration.json')

    def send(self, content, recipients):
        for recipient in recipients:
            s = smtplib.SMTP('localhost')
            msg = self.create_msg('test', 'some message')
            msg['To'] = recipient
            s.sendmail(self.get_address(), recipient, msg.as_string())
            s.quit()

    def load_json(self, filename):
        return json.load(open(filename))

    def get_address(self):
        return self._credentials['sender']

    def create_msg(self, subject, content):
        msg = MIMEText(content)
        msg['From'] = self.get_address()
        msg['Subject'] = self.prepare_subject(subject)
        return msg

    def prepare_subject(self, subject):
        if self._cfg['subject_prefix'] in subject:
            return subject
        return self._cfg['subject_prefix'] + ' ' + subject
