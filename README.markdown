# Deliver

This package is a mailing list manager, that allows sending mails to a
defined group of users. It was born after some time using __Mailman__,
which did not have some customizations that I wanted.

For installation instructions refer to the _INSTALL.markdown_ document.

In a nutshell, _deliver_ offers a simple mailing list, intended for
small user bases, that can be easily adapted to one's needs. Some of the most **special** features are:

### Anonymity

The sent mails don't include the email address of the original
sender(s), neither in the headers nor in the body of the message.

### Custom header/footer

To identify the sender of an email, a custom header is added to each
message with a name or alias for the user. The footer is also
configurable.

### Delivery

Only members of the list are allowed to send messages to the
list. Additionally, a whitelist and a blacklist can be specified, to
add addresses that are outright accepted/rejected. (Manual
confirmation for other addresses is a planned feature)

### Digests

A member can receive messages in digests. Every received message is
archived. Then, at some point, a digest is generated for a user,
containing all the messages pending for the user in text format.

## Configuration

Many options are configurable, via a _config.py_ file. An example file
is included in the distribution under the name
_config.py.example_. The effect of each key is explained there.

## Members List

The members list is stored in a json document. For each user, there is
a number of fields:

1. __name__ - string: The name to identify the user in emails.

2. __aliases__ - list(string): (Optional) list of aliases that can be used
in place of the name. Default is empty.

3. __email__ - dict(string, string): A hash containing the email addresses
for the user, each one identified by a key.

4. __send_to__ - string: (Optional) key of the email to use for the
user. Default value is ''default''.

5. __active__ - boolean: Whether the user should receive emails or not.

6. __digest__ - boolean: (Optional) whether the user should receive emails
in digest mode. Defaults to false.

An example file _members.json.example_ is included in the distribution.
