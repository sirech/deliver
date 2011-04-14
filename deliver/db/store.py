import sys

DB = {
    'sqlite' : 'sqlite'
    }

def choose_backend(backend_name):
    full_name = 'deliver.db.%s' % DB[backend_name]
    __import__(full_name)
    return sys.modules[full_name]

class Store:

    def __init__(self, config):
        self._cfg = {}
        for key in ['type', 'host', 'name', 'user', 'password']:
            self._cfg[key] = config['db_%s' % key]
        self._init_db()

    def _init_db(self):
        module = choose_backend(self._cfg['type'])
        self._db = module.DBWrapper(**self._cfg)


