import argparse
import os

from supay import Daemon
from updater import prepare, loop

curdir = None
def init_d():
    global curdir
    curdir = os.path.abspath(os.path.curdir)
    return Daemon(name='deliver', catch_all_log=curdir, pid_dir=curdir)

def run():
    daemon = init_d()
    daemon.start()
    # Undo some of the changes done by start, otherwise it won't work
    os.chdir(curdir)
    prepare()
    loop()

def restart():
    '''
    Restart only if the process is not already running. To check if
    the daemon is running part of the status functionality is
    reimplemented.

    Using start multiple times is dangerous, as it only checks the
    existence of a pid file, which could be left hanging in case of a
    crash.
    '''
    daemon = init_d()
    try:
        pidfile = open(daemon.pid)
        pid = pidfile.readline()
        os.kill(int(pid), 0)
    except OSError:
        if os.path.isfile(daemon.pid):
            os.remove(daemon.pid)
        run()

def stop():
    daemon = init_d()
    daemon.stop()

def status():
    daemon = init_d()
    daemon.status()

actions = {
    'start' : run,
    'stop' : stop,
    'status' : status,
    'restart' : restart
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Arguments for the deliver daemon')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--start', action='store_const', dest='action', const='start', help='Start the daemon [Default]')
    group.add_argument('--stop', action='store_const', dest='action', const='stop', help='Stop the daemon')
    group.add_argument('--status', action='store_const', dest='action', const='status',
                       help='Consult the status of the daemon')
    group.add_argument('--restart', action='store_const', dest='action', const='restart',
                       help='Restart the daemon, but only if it is not already running')

    # Execute the chosen action
    action = parser.parse_args().action or 'start'
    actions[action]()
