import smtplib
import json

from email.mime.text import MIMEText

class Sender:

    def __init__(self):
        self._creds = json.load(open('credentials.json'))
        self._cfg = json.load(open('configuration.json'))

    def send(self, subject, content, *recipients):
        for recipient in recipients:
            s = smtplib.SMTP(self._creds['smtp_server'])
            msg = self.create_msg(subject, content)
            msg['To'] = recipient
            s.sendmail(self.get_address(), recipient, msg.as_string())
            s.quit()

    def get_address(self):
        return self._creds['sender']

    def create_msg(self, subject, content):
        msg = MIMEText(content)
        msg['From'] = self.get_address()
        msg['Subject'] = self.prepare_subject(subject)
        return msg

    def prepare_subject(self, subject):
        if self._cfg['subject_prefix'] in subject:
            return subject
        return self._cfg['subject_prefix'] + ' ' + subject
