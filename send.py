import smtplib
import json

from email.mime.text import MIMEText

class Sender:

    def __init__(self):
        self._creds = json.load(open('credentials.json'))
        self._cfg = json.load(open('configuration.json'))

    def send_new(self, subject, content, *recipients):
        msg = MIMEText(content)
        msg['Subject'] = self._prepare_subject(subject)
        self._send(msg, *recipients)

    def send(self, msg, *recipients):
        self._send(msg, *recipients)

    def _send(self, msg, *recipients):
        msg.replace_header('Subject', self._prepare_subject(msg['Subject']))
        msg.replace_header('From', self.get_address())
        for recipient in recipients:
            s = smtplib.SMTP(self._creds['smtp_server'])
            msg.replace_header('To', recipient)
            s.sendmail(self.get_address(), recipient, msg.as_string())
            s.quit()

    def get_address(self):
        return self._creds['sender']

    def _prepare_subject(self, subject):
        if self._cfg['subject_prefix'] in subject:
            return subject
        return self._cfg['subject_prefix'] + ' ' + subject
