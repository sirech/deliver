from sqlalchemy import *

from sqlalchemy.orm import mapper, clear_mappers, create_session

from deliver.db.models.message import Message
from deliver.db.models.digest import Digest

class BaseDBWrapper(object):

    def _create_tables(self):

        metadata = MetaData()
        metadata.bind = self.engine
        self.messages = Table('messages', metadata,
                         Column('id', String(256), primary_key=True),
                         Column('content', Text, nullable=False),
                         Column('received_at', DateTime, nullable=False),
                         Column('sent_at', DateTime))

        self.digests = Table('digests', metadata,
                        Column('msg_id', Integer, ForeignKey('messages.id'), primary_key=True),
                        Column('send_to', String(256), primary_key=True),
                        Column('scheduled_at', DateTime, nullable=False),
                        Column('sent_at', DateTime))

        metadata.bind = self.engine
        metadata.create_all(self.engine)

        clear_mappers()
        mapper(Message, self.messages)
        mapper(Digest, self.digests)

        self.session = create_session()
