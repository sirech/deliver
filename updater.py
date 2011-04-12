# This script creates a Distributor and updates its status. As a
# config file, it takes the config.py file that is in the same
# directory.
from config import py
from distribute import Distributor
d = Distributor(py)
d.update()
