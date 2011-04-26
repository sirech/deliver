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
checked starting from version 3.6.19

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

 Other settings are optional, but also recommended.

4. Add a logging configuration. It suffices with a symlink to the
_logging.conf.example_ file. Another link for the _manifest.json_ file
is needed (should be removed in the future).

5. Lastly, copy the files _updater.py_ and _digester.py_ to the
folder. These are used to launch the processing. Symlinking them
doesn't work, sadly.

### Scheduling updates

Right now, _deliver_ works only via cron jobs. _updater.py_ should be
called as often as possible, as it is the one who delivers new
messages. _digester.py_ can be called with less frequency.
