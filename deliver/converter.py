import email
from cStringIO import StringIO
from email.charset import add_charset, Charset, QP
from email.generator import Generator
from email.header import decode_header, Header

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

# Globally replace base64 with quoted-printable
add_charset('utf-8', QP, QP, 'utf-8')

class UnicodeMessage():
    '''
    Wrapper around a email.message.Message, that allows to interact
    with the message using decoded unicode strings.

    Part of the interface to Message is supported. The interface
    methods return normal unicode strings, with the email-specific
    encoding parts removed.

    The underlying message might be transformed by this class and should not
    be used elsewhere.
    '''

    def __init__(self, msg):
        '''
        Create a message that is fully utf-8 encoded.

        msg is the original message.
        '''
        if not isinstance(msg, email.message.Message):
            raise TypeError('msg is not a Message')
        self._msg = msg
        charset = msg.get_content_charset() or 'utf-8'
        self._body_charset = Charset(input_charset=charset)
        assert self._body_charset.header_encoding == QP
        assert self._body_charset.body_encoding == QP

    def __str__(self):
        return self.as_string()

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
        unicode string.

        If the header does not exist, None is returned'''
        value = self._msg[name]
        if value is None:
            return None
        return u''.join(to_unicode(*tupl) for tupl in decode_header(value))

    def replace_header(self, name, value):
        '''Forwards the call to replace_header.

        name the id of the header. If it does not exist yet, it is
        newly created. This behavior is different from the standard
        message.

        value is passed as a unicode string. This method tries to
        avoid encoding the value with a Header (i.e when the value is
        an ascii string).
        '''
        assert isinstance(value, unicode)
        try:
            header = value.encode('ascii')
        except UnicodeEncodeError:
            header = Header(value.encode('utf-8'), 'UTF-8').encode()
        if self._msg.has_key(name):
            self._msg.replace_header(name, header)
        else:
            self._msg.add_header(name, header)

    def get_payload(self, i=None, decode=False):
        '''
        Forwards the call to get_payload.

        Instances of the type email.message.Message are wrapped as a
        UnicodeMessage. Strings are returned as unicode.
        '''
        payload = self._msg.get_payload(i, decode)
        if isinstance(payload, list):
            return [UnicodeMessage(msg) for msg in payload]
        elif isinstance(payload, email.message.Message):
            return UnicodeMessage(payload)
        elif isinstance(payload, str):
            return to_unicode(payload, self._msg.get_content_charset())
        return payload

    def set_payload(self, payload):
        '''
        Forwards the call to set_payload.

        If the payload is text, it is passed as a unicode string. Text
        is encoded again before being passed. The content encoding is
        changed to quoted printable to avoid encoding
        incompatibilities.
        '''
        assert not isinstance(payload, str)
        if isinstance(payload, unicode):
            self.replace_header('Content-Transfer-Encoding', u'quoted-printable')
            payload = self._body_charset.body_encode(
                payload.encode(self._body_charset.input_charset), convert=False)
        self._msg.set_payload(payload)

    from email.Iterators import walk

    def __getattr__(self, name):
        return getattr(self._msg, name)
