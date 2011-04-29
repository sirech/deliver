import email
import urllib2

from datetime import datetime
from cStringIO import StringIO

from email.charset import add_charset, Charset, QP
from email.generator import Generator
from email.header import decode_header, Header
from email.mime.text import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.utils import make_msgid, formatdate

__all__ = ['UnicodeMessage', 'DigestMessage', 'DownloadMessage']

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

class UnicodeMessage(object):
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

def complete_headers(msg, subject, id):
    '''
    Complete the subject, message-id and date headers of a given mail.
    '''
    assert isinstance(msg, UnicodeMessage)
    msg.replace_header('Subject', subject)
    msg.replace_header('Message-Id', to_unicode(make_msgid(id)))
    msg.replace_header('Date', to_unicode(formatdate(localtime=True, usegmt=True)))

def build_text_mail(text):
    '''
    Builds an email that consists of the given text.
    '''
    assert isinstance(text, unicode)
    msg = MIMEText(text.encode('utf-8'), 'plain', 'UTF-8')
    return msg

class DigestMessage(UnicodeMessage):
    '''
    This is a class used to build a digest from a list of emails. All
    the emails are summarized in a single body of plain text. Any
    other attachments or extra content is ignored.
    '''

    def __init__(self, msg_list):
        '''
        Builds a summary mail from the given list and passes it to the
        UnicodeMessage constructor.
        '''
        for msg in msg_list:
            if not isinstance(msg, UnicodeMessage):
                raise TypeError('msg is not a Message')

        super(DigestMessage,self).__init__(self._build_mail(msg_list))
        self._complete_headers()

    def _complete_headers(self):
        '''Fill the headers of the mail'''
        complete_headers(self, u'Digest for %s' % datetime.now(), 'digest')

    def _build_mail(self, msg_list):
        '''Returns a mail that contains all the given mails as a single text'''
        return build_text_mail(self._merge_mails(msg_list))

    def _merge_mails(self, msg_list):
        '''
        Merge the content of all the given mails into one unicode
        string that can be used as the payload of the digest mail.
        '''
        space = u'\n' * 2
        messages = [(msg['Subject'], self._find_text(msg)) for msg in msg_list]
        messages = [u'==== ' + subject + u' ===='
                    + space + payload for subject, payload in messages]
        return (space + (u'*' * 75) + space).join(messages)

    def _find_text(self, msg):
        '''
        Returns the plain text part in a message. If no plain text is
        present, any other text is returned. If there is no text part
        at all, an empty string is returned.

        The text is decoded and returned as an unicode string.
        '''
        fallback = u''
        for part in msg.walk():
            if 'text' ==  part.get_content_maintype():
                if part.get_content_subtype() == 'plain':
                    return part.get_payload(decode=True)
                fallback = part.get_payload(decode=True)
        return fallback

class DownloadMessage(UnicodeMessage):
    '''
    This class is used to build a mail that contains an attachment,
    which is a website downloaded from the given url.
    '''

    def __init__(self, url):
        '''
        Builds a mail, downloading the given url in the process and
        saving it as an attachment.
        '''
        self.url = self._sanitize(url)
        super(DownloadMessage,self).__init__(self._build_mail())
        self._complete_headers()
        pass

    def _sanitize(self, url):
        '''
        Returns the given url as something that can be used by
        urlopen.
        '''
        if not url.startswith('http://'):
            url = 'http://' + url
        return url

    def _complete_headers(self):
        '''Fill the headers of the mail'''
        complete_headers(self, u'Download of %s' % self.url, 'download')

    def _build_mail(self):
        '''
        Download the given url and build an attachment with the
        contents. In case that the download fails, a text mail with
        the error is built instead.
        '''
        success, dl = self._download_url(self.url)
        if not success:
            return build_text_mail(dl)

        msg = MIMEMultipart()
        msg.attach(build_text_mail(u'Downloaded website included as an attachment'))
        part = MIMEBase('application', "octet-stream")
        part.set_payload(dl)
        email.Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % 'website.html')
        msg.attach(part)
        return msg

    def _download_url(self, url):
        '''
        Return a tuple (status, content), with content being the
        content of the url as a string, and status a boolean marking
        whether the download was succesful or not.'''
        try:
            web = urllib2.urlopen(url)
        except Exception as e:
            result = (False, to_unicode(str(e)))
        else:
            result = (True, web.read())
        return result
