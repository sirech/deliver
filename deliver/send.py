import smtplib

import logging
import logging.config

from email.mime.text import MIMEText

logging.config.fileConfig("logging.conf")
logging.getLogger('distribute')

class Sender:
    '''
    Class that is responsible of sending emails. It uses a specified SMTP server.
    '''

    def __init__(self, config):
        self._cfg = config

    def send_new(self, subject, content, *recipients):
        '''
        Creates a new email and sends it to each of the specified recipients.
        The subject and content are given as strings, and are added to a new plain text email.
        '''
        msg = MIMEText(content)
        msg['Subject'] = self._prepare_subject(subject)
        msg['From'] = ''
        msg['To'] = ''
        self._send(msg, *recipients)

    def send(self, msg, *recipients):
        '''
        Sends the given message to each of the specified recipients.
        '''
        self._send(msg, *recipients)

    def _send(self, msg, *recipients):
        '''
        Sends the given message to each of the specified recipients.

        The emails are sent from the specified server, using the specified address. The subject
        is modified to include a subject prefix if it is not already there.
        '''
        msg.replace_header('Subject', self._prepare_subject(msg['Subject']))
        msg.replace_header('From', self.get_address())
        for recipient in recipients:
            logging.debug('Sending message to %s' % recipient)
            s = smtplib.SMTP(self._cfg['smtp_server'])
            msg.replace_header('To', recipient)
            s.sendmail(self.get_address(), recipient, msg.as_string())
            s.quit()

    def get_address(self):
        '''Gets the address used by this sender'''
        return self._cfg['sender']

    def _prepare_subject(self, subject):
        '''Modifies the given subject to include a prefix if it is not already there'''
        if self._cfg['subject_prefix'] in subject:
            return subject
        return self._cfg['subject_prefix'] + ' ' + subject
