import sqlalchemy
from base import BaseDBWrapper

class DBWrapper(BaseDBWrapper):
    '''
    Allows communication with an SQLite DB.
    '''
    def __init__(self, **kws):
        super(DBWrapper,self).__init__()
        self.engine = sqlalchemy.create_engine('sqlite:///:memory:', echo=True, encoding='utf-8')
