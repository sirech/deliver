# -*- coding: utf-8 -*-
import urllib2

from test_base import BaseTest, open_data
from mock import patch, Mock

from deliver.converter import DownloadMessage

class ConverterDownloadTest(BaseTest):
    '''Tests for the DownloadMessage class'''

    def setUp(self):
        super(ConverterDownloadTest,self).setUp()

    def _msg(self, urlopen, url, content):
        if isinstance(content, file):
            content = content.read()
        f = Mock()
        urlopen.return_value = f
        f.read.return_value = content
        return DownloadMessage(url)

    @patch('urllib2.urlopen')
    def test_sanitize(self, urlopen):
        url = 'http://www.google.com'
        msg = self._msg(urlopen, url, '')
        self.assertEqual(msg._sanitize(url), url)

    @patch('urllib2.urlopen')
    def test_sanitize_add_protocol(self, urlopen):
        url = 'www.google.com'
        msg = self._msg(urlopen, url, '')
        self.assertEqual(msg._sanitize(url), 'http://' + url)

    @patch('urllib2.urlopen')
    def test_build_mail(self, urlopen):
        url = 'www.google.com'
        msg = self._msg(urlopen, url, open_data('google.html'))
        self.assertTrue('Download' in msg['Subject'])
        self.assertFalse(msg['Message-Id'] is None)
        self.assertFalse(msg['Date'] is None)
        self.assertTrue(u'multipart/mixed' in msg['Content-Type'] )

        attachment = msg.get_payload(i=1)
        self.assertEqual(attachment['Content-Transfer-Encoding'], 'base64')
        self.assertTrue(attachment.get_payload().startswith(
                u'PCFkb2N0eXBlIGh0bWw+PGh0bWw+PGhlYWQ+PG1ldGEgaHR0cC1lcXVpdj0iY29udGVudC10eXBl'))

    @patch('urllib2.urlopen')
    def test_build_mail_error(self, urlopen):
        urlopen.side_effect = urllib2.HTTPError('', 404, 'Not Found', None, None)
        msg = DownloadMessage('')

        self.assertTrue('Download' in msg['Subject'])
        self.assertFalse(msg['Message-Id'] is None)
        self.assertEqual(msg['Content-Transfer-Encoding'], 'quoted-printable')
        self.assertFalse(msg['Date'] is None)
        self.assertEqual(msg.get_payload(), u'HTTP Error 404: Not Found')
