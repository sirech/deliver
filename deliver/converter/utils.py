from email.mime.text import MIMEText
from email.utils import make_msgid, formatdate

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

def complete_headers(msg, subject, id):
    '''
    Complete the subject, message-id and date headers of a given mail.
    '''
    assert isinstance(subject, unicode)
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
