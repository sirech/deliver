import sqlalchemy

from base import BaseDBWrapper

class DBWrapper(BaseDBWrapper):
    '''
    Allows communication with an Postgresql DB.
    '''
    def __init__(self, **kws):
        super(DBWrapper,self).__init__()
        self.engine = sqlalchemy.create_engine('postgresql://%s:%s@%s/%s' %
                                               (kws['user'], kws['password'], kws['host'], kws['name']),
                                               encoding='utf-8')
        self._create_tables()

    def _table_options(self):
        return {}
