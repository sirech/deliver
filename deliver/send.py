import smtplib

from converter import UnicodeMessage, SummaryMessage

import logging
import logging.config

logging.config.fileConfig("logging.conf")
logging.getLogger('distribute')

class Sender:
    '''
    Class that is responsible of sending emails. It uses a specified SMTP server.
    '''

    def __init__(self, config):
        self._cfg = config

    def send(self, msg, *recipients):
        '''
        Sends the given UnicodeMessage to each of the specified recipients.
        '''
        assert isinstance(msg, UnicodeMessage) or isinstance(msg, SummaryMessage)
        for recipient in recipients:
            assert isinstance(recipient, unicode)
        self._send(msg, *recipients)

    def _send(self, msg, *recipients):
        '''
        Sends the given UnicodeMessage or SummaryMessage to each of
        the specified recipients.

        The emails are sent from the specified server, using the specified address. The subject
        is modified to include a subject prefix if it is not already there.
        '''
        msg.replace_header('Subject', self._prepare_subject(msg['Subject']))
        msg.replace_header('From', self.get_address())
        msg.replace_header('Reply-To', self.get_address())
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
