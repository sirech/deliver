# -*- coding: utf-8 -*-
from test_base import BaseTest, load_msg, load_all_msg
from email.header import decode_header

from deliver.converter import to_unicode, reencode, UnicodeMessage

def convert_all(lst):
    return [UnicodeMessage(msg) for msg in lst]

class ConverterTest(BaseTest):

    def setUp(self):
        super(ConverterTest,self).setUp()
        self.msg = UnicodeMessage(load_msg('sample3'))

    def test_payload_encoding(self):
        for msg in convert_all(load_all_msg()):
            self._test_payload_encoding(msg)

    def _test_payload_encoding(self, msg):
        for part in msg._msg.walk():
            self.assertTrue(part.get_content_maintype() != 'text'
                            or part.get_content_charset() == 'utf-8')

    def test_header_encoding(self):
        for msg in convert_all(load_all_msg()):
            self._test_header_encoding(msg)

    def _test_header_encoding(self, msg):
        for header in msg._msg.values():
            for value, encoding in decode_header(header):
                self.assertTrue(encoding is None or encoding == 'utf-8')
                # should not raise exception
                unicode(value, encoding if encoding is not None else 'ascii')

    def test_get(self):
        self.assertEqual(self.msg['To'], u'sender@host.com')

    def test_get_special_chars(self):
        self.assertEqual(self.msg['Subject'], u'Re: [Test] atensión: los 10 curros mejor pagados!')

    def test_get_nokey(self):
        self.assertEqual(self.msg['Heathen'], None)

    def test_replace_header_ascii(self):
        s = u'Memorias de Adriano'
        self.msg.replace_header('Subject', s)
        self.assertEqual(self.msg['Subject'], s)
        self.assertEqual(self.msg._msg['Subject'], s.encode('ascii'))

    def test_replace_header_special_chars(self):
        s = u'Un día de cólera'
        self.msg.replace_header('Subject', s)
        self.assertEqual(self.msg['Subject'], s)
        self.assertEqual(self.msg._msg['Subject'], '=?utf-8?q?Un_d=C3=ADa_de_c=C3=B3lera?=')
