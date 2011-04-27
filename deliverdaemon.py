import argparse
import os

from supay import Daemon
from updater import prepare, loop

def init_d():
    curdir = os.path.abspath(os.path.curdir)
    return Daemon(name='deliver', catch_all_log=curdir, pid_dir=curdir)

def run():
    daemon = init_d()
    daemon.start(check_pid=True, verbose=True)
    prepare()
    loop()

def stop():
    daemon = init_d()
    daemon.stop(verbose=True)

def status():
    daemon = init_d()
    daemon.status()

actions = {
    'start' : run,
    'stop' : stop,
    'status' : status
    }
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Arguments for the deliver daemon')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--start', action='store_const', dest='action', const='start', help='Start the daemon [Default]')
    group.add_argument('--stop', action='store_const', dest='action', const='stop', help='Stop the daemon')
    group.add_argument('--status', action='store_const', dest='action', const='status',
                        help='Consult the status of the daemon')

    # Execute the chosen action
    action = parser.parse_args().action or 'start'
    actions[action]()
