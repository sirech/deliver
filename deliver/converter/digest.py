from datetime import datetime

from simple import UnicodeMessage
from utils import complete_headers, build_text_mail

class DigestMessage(UnicodeMessage):
    '''
    This is a class used to build a digest from a list of emails. All
    the emails are summarized in a single body of plain text. Any
    other attachments or extra content is ignored.
    '''

    def __init__(self, msg_list):
        '''
        Builds a summary mail from the given list and passes it to the
        UnicodeMessage constructor.
        '''
        for msg in msg_list:
            if not isinstance(msg, UnicodeMessage):
                raise TypeError('msg is not a Message')

        super(DigestMessage,self).__init__(self._build_mail(msg_list))
        self._complete_headers()

    def _complete_headers(self):
        '''Fill the headers of the mail'''
        complete_headers(self, u'Digest for %s' % datetime.now(), 'digest')

    def _build_mail(self, msg_list):
        '''Returns a mail that contains all the given mails as a single text'''
        return build_text_mail(self._merge_mails(msg_list))

    def _merge_mails(self, msg_list):
        '''
        Merge the content of all the given mails into one unicode
        string that can be used as the payload of the digest mail.
        '''
        space = u'\n' * 2
        messages = [(msg['Subject'], self._find_text(msg)) for msg in msg_list]
        messages = [u'==== ' + subject + u' ===='
                    + space + payload for subject, payload in messages]
        return (space + (u'*' * 75) + space).join(messages)

    def _find_text(self, msg):
        '''
        Returns the plain text part in a message. If no plain text is
        present, any other text is returned. If there is no text part
        at all, an empty string is returned.

        The text is decoded and returned as an unicode string.
        '''
        fallback = u''
        for part in msg.walk():
            if 'text' ==  part.get_content_maintype():
                if part.get_content_subtype() == 'plain':
                    return part.get_payload(decode=True)
                fallback = part.get_payload(decode=True)
        return fallback
