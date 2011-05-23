from sqlalchemy import *

from sqlalchemy.orm import mapper, clear_mappers, create_session, relationship, backref

from deliver.db.models.message import Message
from deliver.db.models.digest import Digest

class BaseDBWrapper(object):

    def _create_tables(self):

        metadata = MetaData()
        metadata.bind = self.engine
        self.messages = self._create_table('messages', metadata,
                                           Column('id', String(192), index=True, primary_key=True),
                                           Column('content', Text, nullable=False),
                                           Column('received_at', DateTime, nullable=False),
                                           Column('sent_at', DateTime))

        self.digests = self._create_table('digests', metadata,
                                          Column('msg_id', String(192), ForeignKey('messages.id', ondelete='cascade'),
                                                 primary_key=True),
                                          Column('send_to', String(192), index=True, primary_key=True),
                                          Column('scheduled_at', DateTime, nullable=False),
                                          Column('sent_at', DateTime))

        metadata.bind = self.engine
        metadata.create_all(self.engine)

        clear_mappers()
        mapper(Message, self.messages, properties={
                'digests': relationship(Digest, backref='msg')
                })
        mapper(Digest, self.digests)

        self.session = create_session()

    def __del__(self):
        self.session.close()

    def _create_table(self, name, metadata, *columns):
        return Table(name, metadata, *columns, **self._table_options())
