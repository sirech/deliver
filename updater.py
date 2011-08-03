# This script creates a Distributor and updates regularly its status,
# until a SIGTERM signal is received. The program is not interrupted
# directly, to avoid inconsistent state. As a config file, it takes
# the config.py file that is in the same directory.

import time
import signal

from config import py
from deliver.distribute import OnlineDistributor

import logging
logger = logging.getLogger(__name__)

distributor = None
run = True

def prepare(test_mode=False):
    '''
    Creates a new instance of the distributor. Sets up the signal
    management.

    test_mode (optional) whether the test mode should be used or
    not. If so, the normal reader is replaced with a mock that always
    return zero messages
    '''
    global distributor
    distributor = OnlineDistributor(py)

    if test_mode:
        from mock import Mock
        from deliver.read import Reader
        reader = Mock(spec=Reader)
        reader.new_messages.return_value = []
        distributor._reader = reader

    signal.signal(signal.SIGTERM, terminate)

def update():
    '''Updates the distributor.'''
    return distributor.update()

def sleeping_time(last_time, update_did_something):
    '''
    Gets the length of the next sleep period.

    last_time the length of the last sleep period

    update_did_something whether the updater had any activity in the
    last call or not
    '''
    if update_did_something:
        return py['sleep_after_message']
    else:
        return min(py['sleep_interval'], last_time + py['sleep_increment'])

def loop():
    '''
    Loops indefinitely, updating the distributor and then sleeping for
    a defined time.
    '''
    print 'Starting...'
    sleep = py['sleep_interval']

    try:
        while run:
            success = update()
        sleep = sleeping_time(sleep, success)
        time.sleep(sleep)
    except Exception:
        logging.exception('Oh noes! Exception')

def terminate(signum, frame):
    '''
    Sets a flag that should end the program after the next sleeping
    period is completed.
    '''
    print 'Terminate was called'
    global run
    run = False

if __name__ == '__main__':
    prepare()
    loop()
