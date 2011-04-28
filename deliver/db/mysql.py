from base import BaseDBWrapper

class DBWrapper(BaseDBWrapper):
    '''
    Allows communication with an MySQL DB.
    '''
    def __init__(self, **kws):
        super(DBWrapper,self).__init__()
        self.engine = sqlalchemy.create_engine('mysql+mysqldb://%s:%s@%s/%s?charset=utf8' %
                                               (kws['user'], kws['password'], kws['host'], kws['name']))
        self._create_tables()

    def _table_options(self):
        return {
            'mysql_engine' : 'InnoDB',
            'mysql_charset' : 'utf8'
            }
