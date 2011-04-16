import email
from cStringIO import StringIO
from email.charset import add_charset, Charset, QP
from email.generator import Generator
from email.header import decode_header, make_header, Header

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
    Wrapper around a email.message.Message.

    The message is converted to utf-8 right at the beginning. Part of
    the interface to Message is supported. The interface methods
    return normal unicode strings, with the email-specific encoding
    parts removed.

    The underlying message is transformed by this class and should not
    be used elsewhere.
    '''

    def __init__(self, msg, convert=True):
        '''
        Create a message that is fully utf-8 encoded.

        msg is the original message.

        Optional convert whether the whole message (including
        submessages) should be encoded to utf-8.
        '''
        if not isinstance(msg, email.message.Message):
            raise TypeError('msg is not a Message')
        self._msg = msg
        self._charset = Charset(input_charset='utf-8')
        assert self._charset.header_encoding == QP

        if convert:
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
        '''Forwards the call to replace_header

        The value is passed as a unicode string. This method tries to
        avoid encoding the value with a Header (i.e when the value is
        an ascii string).
        '''
        assert isinstance(value, unicode)
        try:
            header = value.encode('ascii')
        except UnicodeEncodeError:
            header = Header(value.encode('utf-8'), 'UTF-8').encode()
        self._msg.replace_header(name, header)

    def get_payload(self, i=None, decode=False):
        '''
        Forwards the call to get_payload.

        Instances of the type email.message.Message are wrapped as a
        UnicodeMessage. Strings are returned as unicode.
        '''
        payload = self._msg.get_payload(i, decode)
        if isinstance(payload, list):
            return [UnicodeMessage(msg, convert=False) for msg in payload]
        elif isinstance(payload, email.message.Message):
            return UnicodeMessage(payload, convert=False)
        elif isinstance(payload, str):
            return to_unicode(payload)
        return payload

    def set_payload(self, payload):
        '''
        Forwards the call to set_payload.

        If the payload is text, it is passed as a unicode string. Text
        is encoded again before being passed.
        '''
        assert not isinstance(payload, str)
        if isinstance(payload, unicode):
            payload = self._charset.body_encode(payload.encode('utf-8'), convert=False)
        self._msg.set_payload(payload)

    from email.Iterators import walk

    def __getattr__(self, name):
        return getattr(self._msg, name)
