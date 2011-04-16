import sqlalchemy
from base import BaseDBWrapper

class DBWrapper(BaseDBWrapper):
    '''
    Allows communication with an SQLite DB.
    '''
    def __init__(self, **kws):
        super(DBWrapper,self).__init__()
        self.engine = sqlalchemy.create_engine('sqlite:///%s' % kws['name'],
                                               echo=False, encoding='utf-8')
        self._create_tables()
