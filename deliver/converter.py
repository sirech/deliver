import email
from cStringIO import StringIO
from email import Charset
from email.generator import Generator
from email.header import decode_header, make_header

# Globally replace base64 with quoted-printable
Charset.add_charset('utf-8', Charset.QP, Charset.QP, 'utf-8')

def to_unicode(s, encoding=None):
    '''
    Converts the given string to a unicode string using the given
    encoding. If the given encoding is None, utf-8 is used.
    '''
    assert isinstance(s, str)
    return unicode(s, encoding if encoding is not None else 'utf-8')

def reencode(s, encoding=None):
    '''
    Reencodes the given string in the given encoding to utf-8, and
    returns a tuple in the form (encoded_string, 'utf-8').

    The string is converted to unicode (using the given encoding), and
    then converted back to a string using 'utf-8'. If encoding is
    None, the string is returned as is.
    '''
    assert isinstance(s, str)
    if encoding is None:
        return (s, encoding)
    else:
        return (to_unicode(s, encoding).encode('utf-8'), 'utf-8')

class UnicodeMessage:
    '''
    Wrapper around a email.message.Message.

    The message is converted to utf-8 right at the beginning. Part of
    the interface to Message is supported. The interface methods
    return normal unicode strings, with the email-specific encoding
    parts removed.

    The underlying message is transformed by this class and should not
    be used elsewhere.
    '''

    def __init__(self, msg):
        '''
        Create a message that is fully utf-8 encoded.

        The msg is the original message. It is converted to utf-8. All
        the interactions with it should be done through this class.
        '''
        if not isinstance(msg, email.message.Message):
            raise TypeError('msg is not a Message')
        self._msg = msg

        for part in self._msg.walk():
            self._convert_part(part)

    def _convert_part(self, part):
        '''
        Encodes the header and body of the given message part in utf-8.
        '''
        self._convert_header(part)
        self._convert_body(part)

    def _convert_header(self, part):
        '''
        Encodes every already encoded element in the header of this message part in utf-8.

        Elements that are not encoded are left unchanged.
        '''
        for key in part.keys():
            header = make_header(reencode(*tupl) for tupl in decode_header(part[key])).encode()
            part.replace_header(key, header)

    def _convert_body(self, part):
        '''
        If the body of the message part is text, encodes it in utf-8.

        To do this, the set_charset method in the Message class is
        used. It takes care of reencoding the content if necessary.
        '''
        if part.get_content_maintype() == 'text':
            part.set_charset('utf-8')

    def as_string(self):
        """
        Returns the message as a string encoded with utf-8, avoiding the escaping
        of 'From' lines.
        """
        io = StringIO()
        g = Generator(io, False) # second argument means "should I mangle From?"
        g.flatten(self._msg)
        return io.getvalue()

    # Delegate to Message

    def __getitem__(self, name):
        '''Get a header value, from the message, decoded and as a
        unicode string'''
        return u''.join(to_unicode(*tupl) for tupl in decode_header(self._msg[name]))
