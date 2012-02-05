# Installation

This package is intended to run on a linux server. Local
configurations are intended mostly for testing.

## Requirements

1. The package is tested with _Python 2.7_.

2. [http://pypi.python.org/pypi/setuptools](Setuptools) is necessary
to install the package.

## Database

A database is necessary for this software to work. Right now, the
following databases are supported:

1. _SQLite_: Should work out of the box. Foreign keys are properly
checked starting from version 3.6.19.

2. _MySQL_: An adapter needs to be installed, with something like
`easy_install MySQL-python`. The instance of the database needs to be
set up before using _deliver_. It is not necessary to create the
tables, though.

## Installation

Done via _setuptools_. Go to the main directory and do `python setup.py install`. This should make the package available
system-wide. Use `python setup.py develop` to always use the last
version of the code.

## Using deliver

### Creating a new mailing list for an address

Multiple mailing lists can operate in the same machine. To create a
new one, follow these steps:

1. Create a new folder where the list will reside.

2. Copy the _members.json.example_ to the folder, and edit it with the
members of the list.

3. Copy the _config.py.example_ file to the folder, and rename it to
_config.py_. It needs the following edits:

 * __CREDENTIALS__: a valid mail server.
 * __MEMBERS__: the file with the members described above.
 * __DB__: The settings for the database connection.
 * __DAEMON__: How often the daemon tries to get new updates.

 Other settings are optional, but also recommended.

4. Add a logging configuration. It suffices with a symlink to the
_logging.conf.example_ file. Another link for the _manifest.json_ file
is needed (should be removed in the future).

5. Lastly, copy the files _updater.py_, _deliverdaemon.py_ and
_digester.py_ to the folder. These are used to launch the
processing. Symlinking them doesn't work, sadly.

6. For extra notifications, the script _panic_ can also be copied to
the folder.

### Starting deliver

#### Updates

The script _updater.py_ runs in an endless loop, updating the list
according to the settings. This script can be called directly, but is
better to use the daemon _deliverdaemon.py_. It can be simply started
with a command like `python deliverdaemon.py --start` (or with the -h
option for more info). This "daemonizes" the updater script.

It is recommended to set up a cronjob to check if the process is still
alive.

#### Digests

Digests are managed via _digester.py_, which should be called as a
cronjob. The frequency depends on how many digests per day have to be
generated.

#### Auto Restart Daemon

The daemon might die for unexpected reasons. To avoid did, you can set
up a cronjob that automatically restarts the daemon, with a command
like `python deliverdaemon.py --restart`. If the daemon is already
running, no action is performed. The script checks not only the
existence of a _deliver.pid_, but also if the daemon is actually
running.

#### Get notified in case of problems

Even with autorestart, it might happen that the program keeps
crashing, not serving any emails. To be notified in this case, there
is a shell script called _panic_. It can also be set up as a cronjob,
and it checks if the daemon is running. If it is not, an email is sent
to a specified direction to give a warning.

## Running the tests

To run the tests, additional configuration is needed.

 * `sudo apt-get install sqlite`
 * `pip install pysqlite --global-option build_static`
