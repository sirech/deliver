class Digest(object):

    def __init__(self, msg_id, send_to, scheduled_at, sent_at):
        self.msg_id = msg_id
        self.send_to = send_to
        self.scheduled_at = scheduled_at
        self.sent_at = sent_at
