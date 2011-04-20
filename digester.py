# This script creates a Distributor and updates its status. As a
# config file, it takes the config.py file that is in the same
# directory.
from config import py
from deliver.distribute import OfflineDistributor
d = OfflineDistributor(py)
d.update()
