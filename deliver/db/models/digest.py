class Digest(object):

    def __init__(self, msg_id, send_to, scheduled_at, sent_at=None):
        self.msg_id = msg_id
        self.send_to = send_to
        self.scheduled_at = scheduled_at
        self.sent_at = sent_at

    def __repr__(self):
        return '<Digest(msg_id=%s, send_to=%s, scheduled_at=%s, sent_at=%s)>' \
            % (self.msg_id, self.send_to, self.scheduled_at, self.sent_at)
