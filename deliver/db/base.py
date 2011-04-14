from sqlalchemy import Table, Column, Integer, String, Text, DateTime, MetaData, ForeignKey

class BaseDBWrapper(object):

    def create_tables(self):
        metadata = MetaData()
        self.messages = Table('messages', metadata,
                         Column('id', Integer, primary_key=True),
                         Column('content', Text, nullable=False),
                         Column('received_at', DateTime, nullable=False),
                         Column('sent_at', DateTime))

        self.digests = Table('digests', metadata,
                        Column('msg_id', Integer, ForeignKey('messages.id'), nullable=False),
                        Column('to', String(256), nullable=False),
                        Column('scheduled_at', DateTime, nullable=False),
                        Column('sent_at', DateTime))

        metadata.create_all(self.engine)
