import email
from deliver.converter.simple import UnicodeMessage

class Message(object):

    def __init__(self, id, content, received_at, sent_at=None):
        self.id = id
        self.content = content.as_string()
        self.received_at = received_at
        self.sent_at = sent_at

    @property
    def parsed_content(self):
        '''
        Returns the email content as a UnicodeMessage object
        '''
        return UnicodeMessage(
            email.message_from_string(self.content.encode('utf-8')))

    def __repr__(self):
        return '<Message(id=%s, received_at=%s, sent_at=%s)>' \
            % (self.id, self.received_at, self.sent_at)
