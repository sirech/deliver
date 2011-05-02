import email
import urllib2

from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart

from simple import UnicodeMessage
from utils import complete_headers, build_text_mail, to_unicode

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
