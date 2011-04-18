class Message(object):

    def __init__(self, content, received_at, sent_at=None):
        self.content = content
        self.received_at = received_at
        self.sent_at = sent_at
