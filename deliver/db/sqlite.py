import sqlalchemy
from sqlalchemy.interfaces import PoolListener
from sqlalchemy.pool import NullPool

from base import BaseDBWrapper

class DBWrapper(BaseDBWrapper):
    '''
    Allows communication with an SQLite DB.
    '''
    def __init__(self, **kws):
        super(DBWrapper,self).__init__()
        self.engine = sqlalchemy.create_engine('sqlite:///%s' % kws['name'],
                                               echo=False, encoding='utf-8',
                                               poolclass=NullPool,
                                               listeners=[ForeignKeysListener()])
        self._create_tables()

class ForeignKeysListener(PoolListener):
    def connect(self, dbapi_con, con_record):
        db_cursor = dbapi_con.execute('pragma foreign_keys=ON')
